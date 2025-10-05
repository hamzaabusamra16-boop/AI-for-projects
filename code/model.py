from nltk import word_tokenize
import spacy 
from nltk import ngrams
from nltk.tokenize import MWETokenizer  ,sent_tokenize,RegexpTokenizer
from nltk.tokenize.punkt import PunktSentenceTokenizer
import os
import nltk as nl
from nltk.tag import StanfordPOSTagger
from nltk.corpus import stopwords
from nltk.stem.porter import *
from nltk.stem import LancasterStemmer ,WordNetLemmatizer
import pandas as pd
import numpy as np
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import gensim.downloader as api
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression   
from sklearn.tree import DecisionTreeClassifier       
from sklearn.ensemble import RandomForestClassifier   
from sklearn.ensemble import VotingClassifier  
from sklearn.preprocessing import LabelEncoder       
import joblib

def clear_data():
    nlp = spacy.load("en_core_web_sm")
    data = pd.read_csv("df_file.csv")
    data = data.drop_duplicates()
    stop_words = nlp.Defaults.stop_words
    def clear(text):
        text = re.sub(r"[^a-zA-Z0-9 ]", "" ,text)
        text = re.sub(r"http\S+", "" ,text)
        text = re.sub(r"\s+", " " ,text)
        doc = nlp(text)
        return " ".join([token.lemma_ for token in doc if token.text.lower() not in stop_words])
    data["Clrea_Text"] = data["Text"].apply(clear)
    data = data.drop(["Text"],axis=1)
    return data       
    
def tran(data):
    X_text = data.drop(["Label"],axis=1)
    y = data["Label"]
    vectorizer = TfidfVectorizer(strip_accents="unicode",analyzer="word",ngram_range=(1,1),max_features=100000)
    x = vectorizer.fit_transform(X_text["Clrea_Text"])

    model1 =LogisticRegression()
    model2 =DecisionTreeClassifier()
    model3 =RandomForestClassifier()
    model4 =VotingClassifier([
        ("Logistic",model1),("DecisionTree",model2),("RandomForest",model3)
    ])
    X_train, X_test, Y_train, Y_test = train_test_split(x, y, test_size=0.2, random_state=42, shuffle=True)
    model4.fit(X_train,Y_train)
    print(model4.score(X_train,Y_train))
    print(model4.score(X_test,Y_test))
    joblib.dump(model4, "model.pkl")
    return vectorizer
def loop(vectorizer):
    model_loaded = joblib.load("model.pkl")
    nlp = spacy.load("en_core_web_sm")
    print("if you are want to exit write exit()")
    while True:
        uesr = input("write here: ")
        if uesr.lower() == "exit":
            break
        text = uesr
        text = re.sub(r"[^a-zA-Z0-9 ]", "" ,text)
        text = re.sub(r"http\S+", "" ,text)
        text = re.sub(r"\s+", " " ,text)
        doc = nlp(text)
        stop_words = nlp.Defaults.stop_words
        clean_text = " ".join([token.lemma_ for token in doc if token.text.lower() not in stop_words])
        x_test = vectorizer.transform([clean_text])
        y = model_loaded.predict(x_test)
        categories = {0: "Politics", 1: "Sport", 2: "Technology", 3: "Entertainment", 4: "Business"}
        print("Expected classification: ", categories[y[0]])

u = clear_data()
vector = tran(u)
loop( vectorizer=vector)
