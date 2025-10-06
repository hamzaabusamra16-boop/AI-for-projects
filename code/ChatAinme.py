import json
import random
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from keras.models import Sequential, load_model
from tensorflow.keras.optimizers import SGD
from keras.layers import Dense,Dropout

def  clear_data():
    with open("./data/Anime.json","r") as f:
        data = json.load(f)
        Lemmatizer= WordNetLemmatizer()
        words = []
        classes = []
        documents = []
        training = []
        ignore_letters = ["?","!",".",","]
        for intent in data["Anime"]:
            for anime_name , category in intent.items():
                 for cat in category:
                     class_name = f"{anime_name}_{cat['class']}"
                     if class_name not in classes:
                        classes.append(class_name)
                        for question in cat["User_questions"]:
                            token = nltk.word_tokenize(question)
                            token = [w for w in token if w not in ignore_letters ]
                            words.extend(token)
                            documents.append((token,class_name))
        words = [Lemmatizer.lemmatize (word.lower())for word in words if word not in ignore_letters]
        words = sorted(set(words))
        classes =  sorted(set(classes))
        for doc , cls  in documents:
                bag = [0]*len(words)
                for w in doc:
                    w = Lemmatizer.lemmatize(w.lower())
                    for i,word in enumerate(words):
                        if word == w:
                            bag[i]=1
                output_row = [0]*len(classes)
                output_row[classes.index(cls)] = 1
                training.append((bag,output_row))
        random.shuffle(training)
        return training,words,classes
def train_model():
    training,words,classes = clear_data()
    X = [bag for bag ,_ in training]
    Y = [output for _, output in training]
    X = np.array(X)
    Y = np.array(Y)
    model = Sequential()
    model.add(Dense(128, input_shape=(len(X[0]),), activation="relu"))
    model.add(Dropout(0.5))
    model.add(Dense(64,activation="relu"))
    model.add(Dropout(0.5))
    model.add(Dense(len(Y[0]),activation="softmax"))   
    sdg = SGD(learning_rate= 0.01,momentum=0.9,nesterov=True)
    model.compile(loss="categorical_crossentropy",optimizer=sdg,metrics=["accuracy"])
    model.fit(X,Y,epochs=200,batch_size=5,verbose=1)
    model.save("./models/Caht_Anime.keras")
    pickle.dump(words,open("./models/words.pkl","wb"))
    pickle.dump(classes,open("./models/classes.pkl","wb"))

def big_word(user_input):
    with open("./models/words.pkl", "rb") as f:
        words = pickle.load(f)
    Lemmatizer = WordNetLemmatizer()
    token = nltk.word_tokenize(user_input)
    token = [Lemmatizer.lemmatize(word.lower()) for word in token]
    bag = [0] * len(words)
    for w in token:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)

def predict_class(user_input):
    model = load_model("./models/Caht_Anime.keras")
    with open("./models/classes.pkl", "rb") as f:
        classes = pickle.load(f)
    bag = big_word(user_input)
    res = model.predict(np.array([bag]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results_list = []
    for r in results:
        results_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return results_list

def get_respones(user_input):
    with open("./data/Anime.json", "r") as f:
        data = json.load(f)
        results = predict_class(user_input)
        if not results:
            return "Sorry, I didn't understand that."
        tag = results[0]["intent"]
        found = False
        for intent in data["Anime"]:
            for anime_name, category in intent.items():
                for cat in category:
                    class_name = f"{anime_name}_{cat['class']}"
                    if class_name == tag:
                        found = True
                        respones = random.choice(cat["Answer_chat"])
                        return respones
        if not found:
            return "Sorry, I didn't understand that."

def main():

    print("Anime ChatBot - Type your question or 'quit' to exit.")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "quit":
            print("Conversation ended.")
            break
        response = get_respones(user_input)
        print("Bot:", response)


main()