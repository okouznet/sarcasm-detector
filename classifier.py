import pandas as pd
import json_parser
import numpy as np
from sklearn import svm
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

sarcastic_words = ["obviously", "clearly", "totally"]

# sentiment analysis analyzer
sentiment_analyzer = SentimentIntensityAnalyzer()

def make_comment_corpus(data):
    comment_corpus = []
    for i in range(0, len(data)):
        chain = []
        for j in range(0, len(data[i]['chain'])):
            json = data[i]['chain'][j]
            #extract each comment
            if "sarcastic" in json:
                #print json["sarcastic"]
                comment = Comments(body=json["body"], controversiality=json["controversiality"],
                               author=json["author"], ups=json["ups"], downs=json["downs"], label=json["sarcastic"])
                chain.append(comment)
        comment_corpus.append(chain)
    return comment_corpus

class Comments:

    def __init__(self, body, controversiality, author, ups, downs, label):
        self.comment = {}
        self.comment["body"] = body
        self.comment["controversiality"] = controversiality
        self.comment["author"] = author
        self.comment["ups"] = ups
        self.comment["downs"] = downs
        self.comment["label"] = label

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
    """
    :param corpus:list of lists containing Comments objects
    """
    def __init__(self, corpus):
        self.corpus = corpus
        self.features = []

    def sentiment_calculator(self, chain):
        sentiment_feature = []
        avg_sentiment = 0
        #print len(chain)
        for i in range(1, len(chain)): # i corresponds to comment in chain
            body = chain[i].body()

            vs = sentiment_analyzer.polarity_scores(body)
            #deviation = abs(avg_sentiment - vs)
            sentiment_feature.append(avg_sentiment)

            avg_sentiment = (avg_sentiment + vs['compound']) / (i + 1)
        return sentiment_feature

    def get_sentiment_feature(self):
        self.sentiment_feature = []
        for chain in self.corpus:
            chain_sentiment = self.sentiment_calculator(chain=chain)
            for s in chain_sentiment: #remove nested lists
                self.sentiment_feature.append(s)

    def get_literal_features(self):
        self.literal = []
        controversiality = []
        upvotes = []
        downvotes = []

        for chain in self.corpus:
            for comment in chain:
                controversiality.append(int(comment.controversiality))
                upvotes.append(int(comment.ups))
                downvotes.append(int(comment.downs))

        self.literal_features = np.column_stack((controversiality, upvotes, downvotes))


    def get_features(self):
        return self.features

def classifier(X, y):
    clf = svm.SVC()
    clf.fit(X, y)

if __name__ == "__main__":
    file = "sasha-annotated.json"
    data = json_parser.parseJSON(file=file)

    #for i in range(0, len(data)):
        #print data[i]
        #for j in range(0, len(data[i]["chain"])):
           #print data[i]["chain"]

    comment_corpus = make_comment_corpus(data)
    for i in comment_corpus:
        for j in i:
            print j.body()

    features = Features(comment_corpus)
    sentiment = []
    for i in comment_corpus:
        sent = features.sentiment_calculator(i)
        sentiment.append(sent)


    #print sentiment


