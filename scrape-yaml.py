import requests
import json
import time
from pprint import pprint
user_agent_str = 'University of Michigan EECS 498-003 Sarcasm Detector 0.1'

def wait_get(ext):
    r = requests.get('https://www.reddit.com' + ext + '/.json', headers = {'User-agent': 'University of Michigan EECS 498-003 Sarcasm Detector 0.1'})
    while r.status_code == 429:
        time.sleep(2)
        r = requests.get('https://www.reddit.com' + ext + '/.json', headers = {'User-agent': 'University of Michigan EECS 498-003 Sarcasm Detector 0.1'})
    return r.json()

def get_comment_chain(comment_page_link):
    comment_page_link += '/.json'
    r = requests.get(comment_page_link, headers = {'User-agent': 'University of Michigan EECS 498-003 Sarcasm Detector 0.1'})
    while r.status_code == 429:
        r = requests.get(commment_page_link, headers = {'User-agent': 'University of Michigan EECS 498-003 Sarcasm Detector 0.1'})
    data = r.json()
    post = data[0]['data']['children'][0]['data']
    cur_comment = data[1]['data']['children'][0]['data']
    chain = []
    while cur_comment['parent_id'] != cur_comment['link_id']:
        del cur_comment['replies']
        chain.append(cur_comment)
        parent_link = post['permalink'] + cur_comment['parent_id'].split('_')[1]
        cur_comment = wait_get(parent_link)[1]['data']['children'][0]['data']
    del cur_comment['replies']
    chain.append(cur_comment)
    chain = chain[::-1]
    tmp = chain[-1]
    tmp['chain'] = chain[:-1]
    return tmp


chains = []
for comment_page_link in open('../links_post_id.txt').readlines():
    try:
        chains.append(get_comment_chain(comment_page_link))
    except Exception:
        continue
f = open('data.json', 'w')
json.dump(chains, f)
