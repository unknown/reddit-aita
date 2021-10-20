import csv

import pandas as pd

def clean(df):
    df_use = df.copy()
    
    print(f'There are {str(len(df_use))} posts')

    # Remove any edits that may give away the answer [ie, "edit: okay you're right I'm the asshole" ]
    df_use['body'] = df_use['body'].str.replace('(edit|update).*?(YTA|a-|ass|\\sta\\s)(.*)', '', case=False)

    # Replace negative verdict scores with zero
    df_use[df_use['yta_score'] < 0] = 0
    df_use[df_use['nta_score'] < 0] = 0

    # Remove any post with no verdicts
    df_use = df_use[df_use['yta_score'] + df_use['nta_score'] > 10]
    print(f'After removing posts with less than or equal to 10 verdict score, there are {str(len(df_use))} posts left')

    # Remove any deleted or removed posts
    gone_list = ['[deleted]', '[removed]', '']
    df_use = df_use[df_use['body'].str.strip().isin(gone_list) == False]
    df_use = df_use.dropna()
    print(f'After removing empty posts, there are {str(len(df_use))} posts left')

    # Sort by timestamp
    df_use = df_use.sort_values(by=['timestamp'])

    # Create yta and nta percent
    df_use['yta_percent'] = df_use['yta_score'] / (df_use['yta_score'] + df_use['nta_score'])
    df_use['nta_percent'] = 1 - df_use['yta_percent']
    df_use.loc[df_use['yta_percent'] > 0.5, 'verdict'] = 'yta'
    df_use.loc[df_use['yta_percent'] <= 0.5, 'verdict'] = 'nta'

    return df_use

def random_sample(df, n_samples=20000):
    return df.sample(n=n_samples, random_state=1)

def stratified_sample(df, n_samples=20000):
    n = min(n_samples // 2, df['verdict'].value_counts().min())
    df_ = df.groupby('verdict').apply(lambda x: x.sample(n))
    return df_

def main():
    print('Reading data')
    raw = pd.read_csv('1_submission_data_1546300800_1577836800.csv')

    print('Cleaning data')
    clean_data = clean(raw)
    clean_data.to_csv('2_aita_clean.csv', index=False, quoting=csv.QUOTE_ALL)

    print('Sampling data')
    random_data = random_sample(clean_data)
    random_data.to_csv('2_aita_random.csv', index=False, quoting=csv.QUOTE_ALL)

    stratified_data = stratified_sample(clean_data)
    stratified_data.to_csv('2_aita_stratified.csv', index=False, quoting=csv.QUOTE_ALL)

    print('Done')

if __name__ == '__main__':
    main()