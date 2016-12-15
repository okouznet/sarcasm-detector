import json
from sklearn.naive_bayes import MultinomialNB
from pprint import pprint
import random

def make_row(words, word_counts):
    tmp = [0] * len(word_counts)
    i = 0
    for word in word_counts:
        tmp[i] = words.count(word)
        i += 1
    return tmp

def divide_folds(train_vec, y_vec, i):
    fold_size = len(train_vec) / 5
    test_start = i * fold_size
    train_x = train_vec[:test_start] + train_vec[test_start + fold_size:]
    train_y = y_vec[:test_start] + y_vec[test_start + fold_size:]
    test_x = train_vec[test_start : test_start + fold_size]
    test_y = y_vec[test_start : test_start + fold_size]
    return train_x, train_y, test_x, test_y

    

def get_recall(pred, act):
    total = 0
    correct = 0
    for i in range(len(pred)):
        if act[i] == 'y':
            total += 1
            if pred[i] == 'y':
                correct += 1
    return correct / float(total)

def get_precision(pred, act):
    tp = 0
    fp = 0
    for i in range(len(pred)):
        if pred[i] == 'y':
            if act[i] == 'y':
                tp += 1
            else:
                fp += 1
    if tp + fp == 0:
        return 0
    return tp / float(tp + fp)

def get_accuracy(pred, act):
    correct = 0
    total = 0
    for i in range(len(pred)):
        total += 1
        if pred[i] == act[i]:
            correct += 1
    return float(correct) / total


json_files = ['annotated-nikhill.json', 'sasha-annotated.json', 'annotated-jason.json', 'annotated-ari.json']
mnb = MultinomialNB()
vec = []
for file in json_files:
    data = json.load(open(file))
    for chain in data:
        vec.extend(chain['chain'][:])
        del chain['chain']
        vec.append(chain)

train_vec = []
y_vec = []
word_counts = {}
for comment in vec:
    for word in comment['body'].lower().split():
        if word not in word_counts:
            word_counts[word] = 0
        word_counts[word] += 1
i = 0
for comment in vec:
    i += 1
    try:
        train_vec.append(make_row(comment['body'], word_counts))
        y_vec.append(comment['sarcastic'])
    except:
        continue

tmp = zip(train_vec, y_vec)
random.shuffle(tmp)
train_vec, y_vec = zip(*tmp)

test_size = len(train_vec) / 5
recalls = []
accuracies = []
precisions = []
for i in range(5):
    train_x, train_y, test_x, test_y = divide_folds(train_vec, y_vec, i)
    y_pred = mnb.fit(train_x, train_y).predict(test_x)
    recalls.append(get_recall(y_pred, test_y))
    precisions.append(get_precision(y_pred, test_y))
    accuracies.append(get_accuracy(y_pred, test_y))
print recalls
print precisions
print accuracies
print sum(recalls) / float(len(recalls))
print sum(precisions) / float(len(precisions))
print sum(accuracies) / float(len(accuracies))
