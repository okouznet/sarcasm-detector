import json
filename = input("Enter json filename: ")
data = json.load(open(filename))
try:
    for chain in data:
        for comment in chain['chain']:
            if 'sarcastic' in chain['chain']:
                continue
            print(comment['author'] + ':', comment['body'])
            print()
            res = input()
            if res == 'y':
                comment['sarcastic'] = 'y'
            elif res == 'n':
                comment['sarcastic'] = 'n'
            else:
                del comment
                continue
            comment['body'].replace('/s', ' ')
            print('-------------------------')
        if 'sarcastic' in chain:
            continue
        print(chain['author'] + ':', chain['body'])
        print()
        res = input()
        if res == 'y':
            chain['sarcastic'] = 'y'
        elif res == 'n':
            chain['sarcastic'] = 'n'
        else:
            del chain
            continue
        chain['body'].replace('/s', ' ')
        print('===============================')
    outfile = open('data-annotated.json', 'w')
    json.dump(data, outfile)
except:
    outfile = open('data-annotated.json', 'w')
    json.dump(data, outfile)

