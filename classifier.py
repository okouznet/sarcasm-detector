import data
import pandas as pd
import json_parser
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

sarcastic_words = ["obviously", "clearly", "totally"]

def make_comment_corpus(data):
    comment_corpus = []
    for i in range(0, len(data)):
        chain = []
        for j in range(0, len(data[i]['chain'])):
            json = data[i]['chain'][j]
            #extract each comment
            comment = Comments(body=json["body"], controversiality=json["controversiality"],
                               author=json["author"], ups=json["ups"], downs=json["downs"])
            chain.append(comment)
        comment_corpus.append(chain)
    return comment_corpus

class Comments:

    def __init__(self, body, controversiality, author, ups, downs):
        self.comment = {}
        self.comment["body"] = body
        self.comment["controversiality"] = controversiality
        self.comment["author"] = author
        self.comment["ups"] = ups
        self.comment["downs"] = downs
        #self.comment["tag"] = tag

    def body(self):
        return self.comment["body"]

    def ups(self):
        return self.comment["ups"]

    def controversiality(self):
        return self.comment["controversiality"]

    def author(self):
        return self.comment["author"]

    def downs(self):
        return self.comment["downs"]


class Features:
    def __init__(self):
        return

if __name__ == "__main__":
    file = "data-pretty.json"
    data = json_parser.parseJSON(file=file)
    comment_corpus = make_comment_corpus(data)

    for i in comment_corpus:
        for j in i:
            print j.body()



