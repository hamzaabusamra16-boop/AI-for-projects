import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Model , load_model , Sequential
from tensorflow.keras.layers import Input, Embedding, GRU, Dense, Dropout
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle

def prorcess_data():
    with open("./data/chatbot_intent_classification.csv", "r", encoding="utf-8", errors="ignore") as f:
        data_one = pd.read_csv(f)

    with open("./data/df_file.csv", "r", encoding="utf-8", errors="ignore") as f:
        data_two = pd.read_csv(f)

    with open("./data/spam.csv", "r", encoding="latin1", errors="ignore") as f:  
        data_three = pd.read_csv(f)

    with open("./data/train.csv", "r", encoding="utf-8", errors="ignore") as f:
        data_foru = pd.read_csv(f)

    data_foru = data_foru.drop(columns=[
        "selected_text","textID","Time of Tweet","Age of User",
        "Country","Population -2020","Land Area (Km²)","Density (P/Km²)"
    ], errors='ignore')

    data_foru = data_foru.drop(columns=[
        "selected_text","textID","Time of Tweet","Age of User",
        "Country","Population -2020","Land Area (Km²)","Density (P/Km²)"
    ], errors='ignore')

    data_one = data_one.rename(columns={"user_input":"text","intent":"intent"})
    data_two = data_two.rename(columns={"Text":"text","Label":"topic"})
    data_three = data_three.rename(columns={"v1":"spam","v2":"text"})
    data_foru = data_foru.rename(columns={"text":"text","sentiment":"sentiment"})

    data_one["sentiment"] = "neutral"
    data_one["spam"] = "ham"
    data_one["topic"] = "general"

    data_two["sentiment"] = "neutral"
    data_two["spam"] = "ham"
    data_two["intent"] = "none"

    data_three["sentiment"] = "neutral"
    data_three["topic"] = "general"
    data_three["intent"] = "none"

    data_foru["spam"] = "ham"
    data_foru["topic"] = "general"
    data_foru["intent"] = "none"

    data_one = data_one[["text","sentiment","spam","topic","intent"]].astype(str)
    data_two = data_two[["text","sentiment","spam","topic","intent"]].astype(str)
    data_three = data_three[["text","sentiment","spam","topic","intent"]].astype(str)
    data_foru = data_foru[["text","sentiment","spam","topic","intent"]].astype(str)

    data = pd.concat([data_one, data_two, data_three, data_foru], axis=0, ignore_index=True)

    data["text"] = data["text"].astype(str).fillna("unknown")

    le_sentiment = LabelEncoder()
    le_spam = LabelEncoder()
    le_topic = LabelEncoder()
    le_intent = LabelEncoder()

    data["sentiment"] = le_sentiment.fit_transform(data["sentiment"])
    data["spam"] = le_spam.fit_transform(data["spam"])
    data["topic"] = le_topic.fit_transform(data["topic"])
    data["intent"] = le_intent.fit_transform(data["intent"])

    return data, le_sentiment, le_spam, le_topic, le_intent

def train_modelDL():
    data, le_sentiment, le_spam, le_topic, le_intent = prorcess_data()

    texts = data["text"].values
    y_sentiment = data["sentiment"].values
    y_spam = data["spam"].values
    y_topic = data["topic"].values
    y_intent = data["intent"].values

    tokenizer = Tokenizer(num_words=20000, oov_token="<OOV>")
    tokenizer.fit_on_texts(texts)
    sequences = tokenizer.texts_to_sequences(texts)
    max_len = 50
    X = pad_sequences(sequences, maxlen=max_len, padding="post")
    y_sentiment = data["sentiment"].values
    y_spam      = data["spam"].values
    y_topic     = data["topic"].values
    y_intent    = data["intent"].values

    X_train, X_test, y_sentiment_train, y_sentiment_test, y_spam_train, y_spam_test, y_topic_train, y_topic_test, y_intent_train, y_intent_test = train_test_split(
        X, y_sentiment, y_spam, y_topic, y_intent, test_size=0.2, random_state=42
    )

    vocab_size = len(tokenizer.word_index) + 1

    inputs = Input(shape=(max_len,))
    x = Embedding(vocab_size, 128)(inputs)
    x = GRU(128)(x)
    x = Dropout(0.3)(x)

    sentiment_out = Dense(len(le_sentiment.classes_), activation="softmax", name="sentiment")(x)
    spam_out = Dense(len(le_spam.classes_), activation="softmax", name="spam")(x)
    topic_out = Dense(len(le_topic.classes_), activation="softmax", name="topic")(x)
    intent_out = Dense(len(le_intent.classes_), activation="softmax", name="intent")(x)

    model = Model(inputs=inputs, outputs=[sentiment_out, spam_out, topic_out, intent_out])

    model.compile(
        loss="sparse_categorical_crossentropy",
        optimizer="adam",
            metrics={
        "sentiment": "accuracy",
        "spam": "accuracy",
        "topic": "accuracy",
        "intent": "accuracy"
    }

    )

    model.fit(
        X_train,
        {
            "sentiment": y_sentiment_train,
            "spam": y_spam_train,
            "topic": y_topic_train,
            "intent": y_intent_train
        },
        validation_data=(
            X_test,
            {
                "sentiment": y_sentiment_test,
                "spam": y_spam_test,
                "topic": y_topic_test,
                "intent": y_intent_test
            }
        ),
        epochs=40,
        batch_size=32
    )

    model.save("./models/modelDL.h5")
    with open("./models/tokenizer.pkl", "wb") as f:
        pickle.dump(tokenizer, f)
    with open("./models/label_encoders.pkl", "wb") as f:
        pickle.dump((le_sentiment, le_spam, le_topic, le_intent), f)

def main():
    model = load_model("./models/modelDL.h5")
    with open("./models/tokenizer.pkl", "rb") as f:
        tokenizer = pickle.load(f)
    with open("./models/label_encoders.pkl", "rb") as f:
        le_sentiment, le_spam, le_topic, le_intent = pickle.load(f)

    while True:
        text = input("Enter text or 'exit' to quit: ")
        if text.lower() == 'exit':
            break

        seq = tokenizer.texts_to_sequences([text])
        padded = pad_sequences(seq, maxlen=50, padding="post")
        pred = model.predict(padded)

        sentiment = le_sentiment.inverse_transform([pred[0].argmax()])[0]
        spam = le_spam.inverse_transform([pred[1].argmax()])[0]
        topic = le_topic.inverse_transform([pred[2].argmax()])[0]
        intent = le_intent.inverse_transform([pred[3].argmax()])[0]

        print(f"Sentiment: {sentiment}")
        print(f"Spam/Ham: {spam}")
        print(f"Topic: {topic}")
        print(f"Intent: {intent}")

if __name__ == "__main__":
    main()
