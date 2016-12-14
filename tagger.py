import json
filename = input("Enter json filename: ")
data = json.load(open(filename))
try:
    for chain in data:
        print('===============================')
        for comment in chain['chain']:
            print('-------------------------')
            if 'sarcastic' in chain['chain']:
                continue
            print(comment['author'] + ':', comment['body'])
            res = input()
            if res == 'y':
                comment['sarcastic'] = 'y'
            elif res == 'n':
                comment['sarcastic'] = 'n'
            else:
                del comment
                continue
            comment['body'].replace('/s', ' ')
        if 'sarcastic' in chain:
            continue
        print('-------------------------')
        print(chain['author'] + ':', chain['body'])
        res = input()
        if res == 'y':
            chain['sarcastic'] = 'y'
        elif res == 'n':
            chain['sarcastic'] = 'n'
        else:
            del chain
            continue
        chain['body'].replace('/s', ' ')
    outfile = open('annotated-' + filename, 'w')
    json.dump(data, outfile)
except:
    outfile = open('annotated-' + filename, 'w')
    json.dump(data, outfile)

