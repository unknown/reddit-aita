import json
import time
import csv
import requests

import pandas as pd

def get_data(mode, args, fields):
    url = f'http://api.pushshift.io/reddit/{mode}/search/{args}&fields={",".join(fields)}&size=100'
    try:
        r = requests.get(url)
        status = r.status_code
    except Exception as e:
        #print(f'{e} on {proxy["http"]}')
        status = -1
    if status != 200:
        print(f'Error {status}')
        time.sleep(0.5)
        return get_data(mode, args, fields)
    
    #print(f'Fetched data from "{url}" on "{proxy["http"]}"')
    data = json.loads(r.text)
    return data['data']

def get_submissions(subreddit, after, before):
    after, before = str(after), str(before)
    args = f'?after={after}&before={before}&subreddit={subreddit}' + \
           f'&sort=asc&sort_type=created_utc'
    fields = ['id', 'created_utc', 'title', 'selftext', 'author', 'num_comments', 'score']
    
    return get_data('submission', args, fields)

def scrape_submission(submission_data):
    submission_id = submission_data.get('id')
    timestamp = submission_data.get('created_utc')
    title = submission_data.get('title')
    body = submission_data.get('selftext')
    author = submission_data.get('author')
    num_comments = submission_data.get('num_comments')
    score = submission_data.get('score')
    yta_count, nta_count = 0, 0

    data = [submission_id, timestamp, title, body, author, score, num_comments, yta_count, nta_count]

    return data

def scrape_submissions(subreddit, after, before):
    print(f'Scraping submissions of r/{subreddit} from {after} to {before}')

    f_out = open(f'0_submission_data_{after}_{before}.csv', 'w',  newline='', encoding='utf-8') 
    writer = csv.writer(f_out, quoting=csv.QUOTE_ALL)
    header = ['id', 'timestamp', 'title', 'body', 'author', 'score', 'num_comments', 'yta_count', 'nta_count']
    writer.writerow(header)

    scraped_submissions = list()

    while after < before:
        submissions = get_submissions('amitheasshole', after, before)
        if not submissions:
            break

        for submission in submissions:
            scraped_submission = scrape_submission(submission)
            scraped_submissions.append(scraped_submission)

        after = submissions[-1]['created_utc']

        print(f'{len(scraped_submissions)} posts scraped')
    
    print(f'Done scraping submissions of r/{subreddit} from {after} to {before}')
    writer.writerows(scraped_submissions)
    f_out.close()

def main():
    start_epoch = 1546300800 # January 1, 2019
    end_epoch = 1577836800 # January 1, 2020

    scrape_submissions('amitheasshole', start_epoch, end_epoch)

    print('Done')

if __name__ == '__main__':
    main()