from __future__ import division
import json_parser
import numpy as np
from sklearn import svm
from sklearn.tree import DecisionTreeClassifier
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


intensifying_adverbs = ["obviously", "clearly", "totally", "extremely", "absolutely", "hardly"]

# sentiment analysis analyzer
sentiment_analyzer = SentimentIntensityAnalyzer()

"""
Function to parse relevant data out of json file
:param data: data in json format
:return: comment_corpus: list of lists
"""
def make_comment_corpus(data):
    comment_corpus = []
    for i in range(0, len(data)):
        chain = []
        for j in range(0, len(data[i]['chain'])):
            json = data[i]['chain'][j]
            #extract each comment
            if "sarcastic" in json:
                comment = Comments(body=json["body"], controversiality=json["controversiality"],
                               author=json["author"], ups=json["ups"], downs=json["downs"], score=json["score"], label=json["sarcastic"])
                chain.append(comment)
        comment_corpus.append(chain)
    return comment_corpus

"""
Comment class to save all associated data with a comment
"""
class Comments:

    """
    Comments initialization function

    :param body: comment body
    :param controversiality: boolean denoting if comment was controversial or not
    :param author: author of the comment
    :param ups: number of upvotes
    :param downs: number of downvotes
    :param score: difference in upvotes and downvotes
    :param label: 'y' or 'n' marking if comment is sarcastic or not
    """
    def __init__(self, body, controversiality, author, ups, downs, score, label):

        self.comment = {}

        self.comment["controversiality"] = int(controversiality)
        self.comment["author"] = str(author)
        self.comment["ups"] = int(ups)
        self.comment["downs"] = int(downs)
        self.comment["score"] = int(score)

        self.comment["label"] = str(label)

        #normalize body text
        parsed_body = body.encode('ascii', 'ignore')
        parsed_body = parsed_body.replace("/s", "")
        self.comment["body"] = parsed_body

    """
    functions to return comment parameters
    """
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

    def score(self):
        return self.comment["score"]

    def label(self):
        return self.comment["label"]

"""
class for feature extraction
"""
class Features:
    """
    Feature initialization function
    :param corpus:list of lists containing Comments objects
    """
    def __init__(self, corpus):
        self.corpus = corpus
        self.features = []

    """
    function to calculate sentiment for a comment
    :param chain: a comment chain
    :return avg_sentiment: average sentiment before each comment
    :return normal_sentiment: array of sentiment scores for each comment
    """
    def sentiment_calculator(self, chain):
        avg_sentiment = []
        avg = [0]
        normal_sentiment = []
        for i in range(0, len(chain)): # i corresponds to comment in chain
            body = chain[i].body()

            #use Vader sentiment analyzer
            vs = sentiment_analyzer.polarity_scores(body)
            avg_sentiment.append(np.mean(avg))
            avg.append(vs["compound"])
            normal_sentiment.append(vs["compound"])
        return avg_sentiment, normal_sentiment

    """
    function to get all sentiment-related features, including:
    - average sentiment for all preceding comments
    - change in sentiment from previous comment

    :return sentiment_features: vector of sentiment features
    """
    def get_sentiment_features(self):
        avg_sentiment_feature = []
        change_sentiment_feature = []
        prev_sign = 0
        for chain in self.corpus:
            chain_sentiment = self.sentiment_calculator(chain=chain)
            for s in chain_sentiment[0]:
                avg_sentiment_feature.append(s)
            for s in chain_sentiment[1]:
                if (np.sign(s) != prev_sign):
                    change_sentiment_feature.append(1)
                else:
                    change_sentiment_feature.append(0)
                prev_sign = np.sign(s)

        #combine all features into one vector
        sentiment_feature = np.column_stack((avg_sentiment_feature, change_sentiment_feature))
        return sentiment_feature

    """
    function to obtain contextual features
    - parent comment's upvote-downvote difference
    - change in sign of upvote-downvote difference
    :return: context_features: vector of contextua features
    """
    def get_contextual_features(self):
        parent_score = []
        prev_score = 0
        prev_sign = 0
        sign_feature = []
        for chain in self.corpus:
            for comment in chain:
                curr_sign = np.sign(comment.score())
                if curr_sign != prev_sign:
                    sign_feature.append(1)
                else:
                    sign_feature.append(0)
                parent_score.append(comment.score())
                prev_score = comment.score()
                prev_sign = curr_sign
        context_features = np.column_stack((parent_score, sign_feature))
        return context_features

    """
    function to obtain literal features, including
    - controversiality
    - upvotes
    - downvotes
    - intensity
    :return literal_features: vector of literal features
    """
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
                        break
                intensity.append(intensity_present)

        literal_features = np.column_stack((controversiality, upvotes, downvotes, intensity))
        return literal_features

    """
    function to obtain visual features, including:
    - presence of emojis
    - presence of bolded words
    - presence of uppercase words
    :return visual_features: vector of visual features
    """
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

    """
    function to obtain labels
    - 0 = not sarcastic
    - 1 = sarcastic
    :return labels
    """
    def get_labels(self):
       labels = []
       for chain in self.corpus:
            for comment in chain:
                if comment.label() == "y":
                    labels.append(1)
                else:
                    labels.append(0)
       return labels

    """
    driver function to obtain all features:
    - literal
    - sentiment-oriented
    - contextual
    - visual
    :return features: feature vector
    """
    def get_features(self):
        self.literal = self.get_literal_features()
        self.sentiment = self.get_sentiment_features()
        self.visual = self.get_visual_features()
        self.context = self.get_contextual_features()
        features = np.column_stack((self.literal, self.sentiment, self.visual))
        return features

"""
SVM Classifier
"""
def svm_classifier(X, y, XTest, ytest):
    #clf = svm.SVC()
    clf = svm.SVC(probability=True)
    clf.fit(X, y)
    predicted = clf.predict(XTest)

    count = 0
    for i in range(0, len(predicted)):
        if predicted[i] == ytest[i]:
            count  = count + 1

    print "SVM Accuracy: " + str(count / len(predicted))
    return predicted



"""
Decision Tree Classifier
"""
def decision_tree_classifier(X, y, XTest, ytest):
    clf = DecisionTreeClassifier(criterion="entropy")
    clf.fit(X, y)
    predicted = clf.predict(XTest)
    score = clf.score(XTest, ytest)
    print "Decision Tree Accuracy: " + str(score * 100) + "%"
    return predicted

"""
Function to calculate recall (#correct sarcastic labels / total sarcastic labels)
"""
def recall(predicted, actual):
    numerator = 0
    denominator = 0
    for i in range(0, len(predicted)):
        if actual[i] == 1:
            denominator += 1
        if predicted[i] == 1 and actual[i] == 1:
            numerator += 1
    print "Recall: " + str(numerator / denominator)
    return (numerator / denominator)

"""
Baseline function: label all data as 'not sarcastic'
"""
def baseline(actual):
    count = 0
    for i in range(0, len(actual)):
        if actual[i] == 0:
            count += 1
    baseline = count / len(actual)
    print "Baseline: " + str(baseline)
    return baseline


if __name__ == "__main__":

    #obtain training data
    train_data = json_parser.parseJSON(file="annotated-anj.json")
    train_corpus = make_comment_corpus(train_data)

    f_train= Features(train_corpus)
    #obtain feature vector and labels for training data
    training_features = f_train.get_features()
    training_labels = f_train.get_labels()

    #obtain test data
    test_data = json_parser.parseJSON(file="sasha-annotated.json")
    test_corpus = make_comment_corpus(test_data)
    f_test = Features(test_corpus)
    test_labels = f_test.get_labels()
    test_features = f_test.get_features()

    #run SVM classifier
    predicted_svm = svm_classifier(X=training_features, y=training_labels, XTest=test_features, ytest=test_labels)

    #run Decision Tree Classifier
    predicted_tree = decision_tree_classifier(X=training_features, y=training_labels, XTest=test_features, ytest=test_labels)

    recall(predicted=predicted_tree, actual=test_labels)
    baseline(test_labels)