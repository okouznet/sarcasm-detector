from __future__ import division
import pandas as pd
import json_parser
import numpy as np
from sklearn import svm
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

intensifying_adverbs = ["obviously", "clearly", "totally", "extremely", "absolutely", "so", "hardly"]

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
        self.comment["body"] = body.encode('ascii', 'ignore')
        self.comment["controversiality"] = int(controversiality)
        self.comment["author"] = str(author)
        self.comment["ups"] = int(ups)
        self.comment["downs"] = int(downs)
        self.comment["label"] = str(label)

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

    def label(self):
        return self.comment["label"]


class Features:
    """
    :param corpus:list of lists containing Comments objects
    """
    def __init__(self, corpus):
        self.corpus = corpus
        self.features = []

    def sentiment_calculator(self, chain):
        sentiment_feature = []
        avg_sentiment = [0] #CHANGE
        #print len(chain)
        for i in range(0, len(chain)): # i corresponds to comment in chain
            body = chain[i].body()
            vs = sentiment_analyzer.polarity_scores(body)

            sentiment_feature.append(np.mean(avg_sentiment))
            avg_sentiment.append(vs["compound"])
            #avg_sentiment + vs['compound']) / (i + 2)
        return sentiment_feature

    def get_sentiment_features(self):


        avg_sentiment_feature = []
        for chain in self.corpus:
            chain_sentiment = self.sentiment_calculator(chain=chain)
            for s in chain_sentiment: #remove nested lists
                avg_sentiment_feature.append(s)
        return avg_sentiment_feature

    def get_literal_features(self):

        controversiality = []
        upvotes = []
        downvotes = []
        intensity = []
        for chain in self.corpus:
            for comment in chain:
                controversiality.append((comment.controversiality()))
                upvotes.append((comment.ups()))
                downvotes.append((comment.downs()))
                intensity_present = 0
                lower = comment.body()
                for word in intensifying_adverbs:
                    if word in lower.lower():
                        intensity_present = 1
                        print word
                        break
                intensity.append(intensity_present)

        literal_features = np.column_stack((controversiality, upvotes, downvotes, intensity))
        return literal_features

    def get_visual_features(self):
        emoticon_feature = []
        bold_feature = []
        all_capitals_feature = []
        for chain in self.corpus:
            for comment in chain:
                if ":)" in comment.body():
                    emoticon_feature.append(1)
                else:
                    emoticon_feature.append(0)
                if comment.body().isupper():
                    all_capitals_feature.append(1)
                else:
                    all_capitals_feature.append(0)
                if "**" in comment.body():
                    bold_feature.append(1)
                else:
                    bold_feature.append(0)
        visual_features = np.column_stack((emoticon_feature, bold_feature, all_capitals_feature))
        return visual_features

    def get_labels(self):
       labels = []
       for chain in self.corpus:
            for comment in chain:
                if comment.label() == "y":
                    labels.append(1)
                else:
                    labels.append(0)
       return labels

    def get_features(self):
        self.literal = self.get_literal_features()
        self.sentiment = self.get_sentiment_features()
        self.visual = self.get_visual_features()
        #print self.sentiment
        features = np.column_stack((self.literal, self.sentiment, self.visual))
        return features

def baseline():
    return

def svm_classifier(X, y, XTest, ytest):
    #clf = svm.SVC()
    clf = svm.SVC(probability=True)
    clf.fit(X, y)
    predicted = clf.predict(XTest)
    print predicted
    print ytest
    count = 0
    for i in range(0, len(predicted)):
        if predicted[i] == ytest[i]:
            count  = count + 1

    print "Accuracy: " + str(count / len(predicted))


if __name__ == "__main__":
    file = "annotated-nikhill.json"
    data = json_parser.parseJSON(file=file)

    test_data = json_parser.parseJSON(file="sasha-annotated.json")
    comment_corpus = make_comment_corpus(data)


    features = Features(comment_corpus)
    sentiment = []
    for i in comment_corpus:
        sent = features.sentiment_calculator(i)
        sentiment.append(sent)
    training_features = features.get_features()
    training_labels = features.get_labels()


    #print sentiment

    test_corpus = make_comment_corpus(test_data)
    f = Features(test_corpus)
    test_labels = f.get_labels()
    test_features = f.get_features()

    svm_classifier(X=training_features, y=training_labels, XTest=test_features, ytest=test_labels)


