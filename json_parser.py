import json


def parseJSON(file):
    with open(file) as data_file:
        data = json.load(data_file)
    #pprint(data)
    return data

if __name__ == "__main__":

    file = "data-pretty.json"
    data = parseJSON(file=file)

    """
    example of extracting all comments from chains
    i = number of chains
    j = comment in each chain
    """
    for i in range(0, len(data)):
        for j in range(0, len(data[i]['chain'])):
            print data[i]['chain'][j]['body']