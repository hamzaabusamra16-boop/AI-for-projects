import random
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from keras.models import Sequential, load_model
from tensorflow.keras.optimizers import SGD
from keras.layers import Dense,Dropout

def main():
    def clrea_data():
        with open("./data/data.json",encoding="utf-8") as f:
            data = json.load(f)
        words =[]
        classes = []
        document = []
        training = []
        Lemmatizer=WordNetLemmatizer()
        for i in data["data"]:
               for aks in i["User_questions"]  :
                    tokens = nltk.word_tokenize(aks.lower())
                    words.extend(tokens) 
                    document.append((tokens,i["clas"]))
               if i["clas"] not in classes:
                    classes.append(i["clas"])
        words = [Lemmatizer.lemmatize(w.lower()) for w in words]  
        words = sorted(list(set(words)))  
        classes = sorted(list(set(classes)))                    
        for tokens, cls in document:
                bag = [0] * len(words)
                for token in tokens:
                    if token in words:
                        index = words.index(token)
                        bag[index] = 1

                output_row = [0] * len(classes)
                output_row[classes.index(cls)] = 1
                training.append((bag, output_row))
        random.shuffle(training)
        return training,classes,words,document
    def train_data():
          training,classes,words,document= clrea_data()
          x = np.array([bag for bag, _ in training])
          y = np.array([output for _, output in training])
          model = Sequential()
          model.add(Dense(128,input_shape=(len(x[0]),), activation="relu"))
          model.add(Dropout(0.2))
          model.add(Dense(64, activation="relu"))
          model.add(Dropout(0.2))
          model.add(Dense(32, activation="relu"))
          model.add(Dropout(0.2))
          model.add(Dense(len(y[0]), activation="softmax"))
          sdg = SGD(learning_rate = 0.01 ,momentum = 0.9,nesterov = True )
          model.compile(loss="categorical_crossentropy", optimizer=sdg, metrics=["accuracy"])
          model.fit(x, y, epochs=200, batch_size=8, verbose=1)
          model.save("chat_bot.keras")
          with open("classes.pkl", "wb") as f:
                pickle.dump(classes, f)
          with open("words.pkl", "wb") as f:
                pickle.dump(words, f)
    def uesr():
        Lemmatizer=WordNetLemmatizer()
        model = load_model("./models/chat_bot.keras")
        with open("./models/words.pkl", "rb") as f:
               words = pickle.load(f) 
        with open("./models/classes.pkl","rb") as f:
               classes = pickle.load(f) 
        with open("./data/data.json",encoding="utf-8") as f:
                        data = json.load(f)
        def clearn(y):
                words_angin = nltk.word_tokenize(y)
                words_angin = [Lemmatizer.lemmatize(i) for i in words_angin]
                return words_angin
        def  big_word(y):
                words_angin = clearn(y)
                bag = [0]* len(words)
                for w in words_angin:
                    if w in words:
                         index = words.index(w)
                         bag[index]=1
                return np.array(bag)
        def big_classes(y):
                BigWord = big_word(y)
                clas = model.predict(np.array([BigWord]))[0]
                ERROR_THRESHOLD = 0.50
                results = [[i, r] for i, r in enumerate(clas) if r > ERROR_THRESHOLD]
                resutil_list=[]
                for w in results:
                    resutil_list.append({"intent": classes[w[0]], "probability": str(w[1])})
                return resutil_list
        def responses(y):
                 resutil_list = big_classes(y)
                 if resutil_list:
                      tag = resutil_list[0]["intent"]
                      for i in data["data"]:
                           if i["clas"] == tag:
                                return random.choice(i["Answer_chat"])
                 return "I didn't understand that."
        while True:
            msg = input("You: ")
            if msg.lower() == "exit":
                break
            print("Bot:", responses(msg))

    uesr()   
main()