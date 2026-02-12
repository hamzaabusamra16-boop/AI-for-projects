from nltk import word_tokenize
import spacy as sp
from nltk import ngrams
from nltk.tokenize import MWETokenizer  ,sent_tokenize
from nltk.tokenize.punkt import PunktSentenceTokenizer
import os
import nltk as nl
from nltk.tag import StanfordPOSTagger
from nltk.corpus import stopwords
from nltk.stem.porter import *
from nltk.stem import LancasterStemmer
java_path = "/Library/Java/JavaVirtualMachines/jdk-25.jdk/Contents/Home/bin/java"
os.environ["JAVA_HOME"] = java_path

jar = "/Users/hamzaabusamra/Downloads/stanford-postagger-full-2018-10-16/stanford-postagger-3.9.2.jar"
model = "/Users/hamzaabusamra/Downloads/stanford-postagger-full-2018-10-16/models/english-bidirectional-distsim.tagger"

with open("nlp_large_test_data.txt", encoding="utf-8") as f:
      data = f.read()
text = word_tokenize(data)
mwe = MWETokenizer([("Artificial","intelligence"),("Deep","learning")],separator=" ")
t = mwe.tokenize(text)
cler_text =set (stopwords.words("english"))
text_data = []
for i in text:
      if i.lower() not in cler_text:
          text_data.append(i)
lan = LancasterStemmer()
words = [x for x in text_data]
for i in words:
     print(i)    
pos_tagger = StanfordPOSTagger(model, jar, encoding="utf-8")
text_pos = pos_tagger.tag(words)  # هنا نمرر قائمة الكلمات
for test , tag in text_pos:
    print(test, "->", tag)
    
