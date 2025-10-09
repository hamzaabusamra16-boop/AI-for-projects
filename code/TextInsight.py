import pandas as pd
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Input, Embedding, GRU, Dense, Dropout, TimeDistributed
from tensorflow.keras.utils import to_categorical
import numpy as np
import pickle

def proprecessing_data():
    def load_data():
        with open("./data/train.txt","r",encoding="utf-8") as f:
            lines = f.readlines()
        part_one = pd.read_csv("./data/BBC News Train.csv")
        part_two = pd.read_csv("./data/train.csv").head(10000)
        part_three = pd.read_csv("./data/IMDB Dataset.csv")
        return lines, part_one, part_two, part_three

    def clean_data():
        lines, part_one, part_two, part_three = load_data()

        def extract_entities():
            entities = {"PER": [], "LOC": [], "ORG": [], "MISC": []}
            current_entity = []
            current_type = None

            for line in lines:
                line = line.strip()
                if line == "":
                    if current_entity and current_type:
                        entities[current_type].append(" ".join(current_entity))
                        current_entity = []
                        current_type = None
                    continue
                parts = line.split()
                if len(parts) != 4:
                    continue
                word, pos, chunk, ner = parts
                if ner == "O":
                    if current_entity and current_type:
                        entities[current_type].append(" ".join(current_entity))
                        current_entity = []
                        current_type = None
                elif ner.startswith("B-"):
                    if current_entity and current_type:
                        entities[current_type].append(" ".join(current_entity))
                    current_type = ner[2:]
                    current_entity = [word]
                elif ner.startswith("I-") and current_type:
                    current_entity.append(word)
            if current_entity and current_type:
                entities[current_type].append(" ".join(current_entity))
            return entities

        entities = extract_entities()

        part_one_clean = part_one.rename(columns={"Text": "text", "Category": "label"})
        part_two_clean = part_two.rename(columns={"article": "text", "highlights": "label"})
        part_three_clean = part_three.rename(columns={"review": "text", "sentiment": "label"})

        for df, default_sentiment in zip([part_one_clean, part_two_clean, part_three_clean],
                                         ["neutral", "neutral", None]):
            df["sentiment"] = default_sentiment if default_sentiment else df["label"]
            df["topic"] = "general"
            df["intent"] = "none"
            df["spam"] = "ham"

        columns_to_drop = ["ArticleId", "id", "article", "highlights"]
        for df in [part_one_clean, part_two_clean, part_three_clean]:
            for col in columns_to_drop:
                if col in df.columns:
                    df.drop(col, axis=1, inplace=True)

        data = pd.concat([part_one_clean, part_two_clean, part_three_clean], axis=0)
        return data, entities

    return clean_data()

def train_model():
    def create_ner_labels_from_data(data, max_len=50):
        ner_labels = []
        le_ner = LabelEncoder()

        all_labels = []
        for text in data["text"]:
            words = text.split()
            labels = ["O"] * len(words)  
            ner_labels.append(labels)
            all_labels.extend(labels)

        le_ner.fit(all_labels)

        ner_sequences = [le_ner.transform(sent) for sent in ner_labels]

        ner_sequences_padded = pad_sequences(ner_sequences, maxlen=max_len, padding='post', value=le_ner.transform(["O"])[0])

        y_ner = to_categorical(ner_sequences_padded, num_classes=len(le_ner.classes_))

        return y_ner, le_ner

    def read_data():
        data, entities = proprecessing_data()
        return data, entities

    def model():
        data, entities = read_data()

        tokenizer = Tokenizer(num_words=5000, oov_token="<OOV>")
        tokenizer.fit_on_texts(data["text"])
        x_seq = tokenizer.texts_to_sequences(data["text"])
        x_pad = pad_sequences(x_seq, maxlen=50, padding="post")

        y_ner, le_ner = create_ner_labels_from_data(data, max_len=50)

        le_summary = LabelEncoder()
        y_summary = to_categorical(le_summary.fit_transform(data["label"]))

        le_topic = LabelEncoder()
        y_topic = to_categorical(le_topic.fit_transform(data["topic"]))

        le_sentiment = LabelEncoder()
        y_sentiment = to_categorical(le_sentiment.fit_transform(data["sentiment"]))

        x_train, x_test, y_train_summary, y_test_summary = train_test_split(
            x_pad, y_summary, test_size=0.2, random_state=42, shuffle=True
        )
        _, _, y_train_topic, y_test_topic = train_test_split(
            x_pad, y_topic, test_size=0.2, random_state=42, shuffle=True
        )
        _, _, y_train_sentiment, y_test_sentiment = train_test_split(
            x_pad, y_sentiment, test_size=0.2, random_state=42, shuffle=True
        )
        _, _, y_train_ner, y_test_ner = train_test_split(
            x_pad, y_ner, test_size=0.2, random_state=42, shuffle=True
        )

        MAX_WORDS = 5000
        MAX_LEN = 50
        EMBED_DIM = 128

        input_text = Input(shape=(MAX_LEN,), name="input_text")
        x = Embedding(input_dim=MAX_WORDS, output_dim=EMBED_DIM, input_length=MAX_LEN)(input_text)
        x = GRU(128, return_sequences=True)(x)
        x = Dropout(0.5)(x)
        x2 = GRU(64)(x)

        summary_output = Dense(y_summary.shape[1], activation="softmax", name="summary_output")(x2)
        topic_output = Dense(y_topic.shape[1], activation="softmax", name="topic_output")(x2)
        sentiment_output = Dense(y_sentiment.shape[1], activation="softmax", name="sentiment_output")(x2)
        ner_output = TimeDistributed(Dense(len(le_ner.classes_), activation="softmax"), name="ner_output")(x)

        model = Model(inputs=input_text, outputs=[summary_output, topic_output, sentiment_output, ner_output])
        model.compile(
            optimizer="adam",
            loss={
                "summary_output": "categorical_crossentropy",
                "topic_output": "categorical_crossentropy",
                "sentiment_output": "categorical_crossentropy",
                "ner_output": "categorical_crossentropy"
            },
            metrics={
                "summary_output": "accuracy",
                "topic_output": "accuracy",
                "sentiment_output": "accuracy",
                "ner_output": "accuracy"
            }
        )

        # --- تدريب الموديل ---
        model.fit(
            x_train,
            {
                "summary_output": y_train_summary,
                "topic_output": y_train_topic,
                "sentiment_output": y_train_sentiment,
                "ner_output": y_train_ner
            },
            validation_data=(
                x_test,
                {
                    "summary_output": y_test_summary,
                    "topic_output": y_test_topic,
                    "sentiment_output": y_test_sentiment,
                    "ner_output": y_test_ner
                }
            ),
            epochs=20,
            batch_size=32
        )

        with open('./models/tokenizer.pkl', 'wb') as f:
            pickle.dump(tokenizer, f)
        with open('./models/le_summary.pkl', 'wb') as f:
            pickle.dump(le_summary, f)
        with open('./models/le_topic.pkl', 'wb') as f:
            pickle.dump(le_topic, f)
        with open('./models/le_sentiment.pkl', 'wb') as f:
            pickle.dump(le_sentiment, f)
        with open('./models/le_ner.pkl', 'wb') as f:
            pickle.dump(le_ner, f)

        # --- حفظ الموديل ---
        model.save("./models/model_projact_Two.keras")

    model()

# ---------------------------
# 3️⃣ تجربة الموديل
# ---------------------------
def mean():
    model = load_model("./models/model_projact_Two.keras")

    with open('./models/tokenizer.pkl', 'rb') as f:
        tokenizer = pickle.load(f)
    with open('./models/le_summary.pkl', 'rb') as f:
        le_summary = pickle.load(f)
    with open('./models/le_topic.pkl', 'rb') as f:
        le_topic = pickle.load(f)
    with open('./models/le_sentiment.pkl', 'rb') as f:
        le_sentiment = pickle.load(f)
    with open('./models/le_ner.pkl', 'rb') as f:
        le_ner = pickle.load(f)

    while True:
        text = input("Enter text (type 'exit' to quit): ")
        if text.lower() == "exit":
            break

        seq = tokenizer.texts_to_sequences([text])
        padded = pad_sequences(seq, maxlen=50, padding="post")

        summary_pred, topic_pred, sentiment_pred, ner_pred = model.predict(padded, verbose=0)

        summary_class = le_summary.inverse_transform([np.argmax(summary_pred)])[0]
        topic_class = le_topic.inverse_transform([np.argmax(topic_pred)])[0]

        sentiment_idx = np.argmax(sentiment_pred)
        sentiment_class = le_sentiment.inverse_transform([sentiment_idx])[0]

        ner_indices = np.argmax(ner_pred, axis=2)[0]
        ner_class = [le_ner.classes_[i] for i in ner_indices]

        print(f"Summary class: {summary_class}")
        print(f"Topic class: {topic_class}")
        print(f"Sentiment class: {sentiment_class}")
        print(f"NER classes per word: {ner_class}")

train_model()
