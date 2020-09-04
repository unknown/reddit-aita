import json
import time
import string
import csv
import itertools
import requests

import pandas as pd
import numpy as np

from tqdm import tqdm
from multiprocessing import Pool
from proxies import random_proxy, remove_proxy

def get_data(mode, args, fields):
    url = f'http://api.pushshift.io/reddit/{mode}/search/{args}&fields={",".join(fields)}&size=100'
    proxy = random_proxy()
    timeout = (3, 7)
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

    try:
        r = requests.get(url, proxies=proxy, timeout=timeout, headers=headers, allow_redirects=False)
        status = r.status_code
    except Exception as e:
        #print(f'{e} on {proxy["http"]}')
        status = -1
    if status != 200:
        #if status != -1:
            #print(f'{status} on {proxy["http"]}')
        #remove_proxy(proxy['http'])
        time.sleep(0.25)
        return get_data(mode, args, fields)
    
    #print(f'Fetched data from "{url}" on "{proxy["http"]}"')
    data = json.loads(r.text)
    return data['data']

def get_comments(id, after):
    after = str(after)
    args = f'?after={after}&link_id={id}' + \
           f'&sort=asc&sort_type=created_utc'
    fields = ['created_utc', 'body', 'author']

    return get_data('comment', args, fields)

def get_all_comments(id):
    after = 0
    comments = list()

    while True:
        new_comments = get_comments(id, after)
        if not new_comments:
            break

        for comment in new_comments:
            comment_data = {
                'timestamp': comment['created_utc'],
                'text': comment['body'],
                'author': comment['author']
            }
            comments.append(comment_data)

        after = comments[-1]['timestamp']
    
    return comments
    
def scrape_comment(submission_data):
    # data = [submission_id, timestamp, title, body, author, score, num_comments, yta_count, nta_count]
    yta_count, nta_count = 0, 0

    if int(submission_data['num_comments']) > 0:
        comments = get_all_comments(submission_data['id'])
        for comment in comments:
            if comment['author'].lower() == 'automoderator':
                continue
            comment_text = comment['text'].translate(str.maketrans('', '', string.punctuation))
            words = comment_text.lower().split()
            if 'yta' in words or 'esh' in words:
                yta_count += 1
            if 'nta' in words or 'nah' in words:
                nta_count += 1
    
    submission_data['yta_count'] = yta_count
    submission_data['nta_count'] = nta_count

    return submission_data

def scrape_commments(subreddit, after, before):
    print(f'Scraping comments of r/{subreddit} from {after} to {before}')

    f_out = open(f'1_submission_data_{after}_{before}.csv', 'w',  newline='', encoding='utf-8') 
    header = ['id', 'timestamp', 'title', 'body', 'author', 'score', 'num_comments', 'yta_count', 'nta_count']
    writer = csv.DictWriter(f_out, quoting=csv.QUOTE_ALL, fieldnames=header)
    writer.writeheader()

    processes = 32
    submissions = list()
    scraped_submissions = list()
    
    with open(f'0_submission_data_{after}_{before}.csv', 'r',  newline='', encoding='utf-8') as f_in:
        reader = csv.DictReader(f_in)
        for row in reader:
            submissions.append(row)

    p = Pool(processes=processes)

    with tqdm(total=len(submissions)) as progressbar:
        for entry in enumerate(p.imap_unordered(scrape_comment, submissions)):
            scraped_submissions.append(entry)
            progressbar.update()
    
    p.close()
    print(f'Done scraping comments of r/{subreddit} from {after} to {before}')
    
    for row in scraped_submissions:
        writer.writerow(row[1])
    f_out.close()

def main():
    start_epoch = 1546300800 # January 1, 2019
    end_epoch = 1577836800 # January 1, 2020

    scrape_commments('amitheasshole', start_epoch, end_epoch)

    print('Done')

if __name__ == '__main__':
    main()