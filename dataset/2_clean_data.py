import csv

import pandas as pd

def clean_data(df):
    df_use = df.copy()
    
    print(f'There are {str(len(df_use))} posts')

    # Remove any edits that may give away the answer [ie, "edit: okay you're right I'm the asshole" ]
    df_use['body'] = df_use['body'].str.replace('(edit|update).*?(YTA|a-|ass|\\sta\\s)(.*)', '', case=False)

    # Remove any post with no verdicts
    df_use = df_use.loc[df_use['yta_count'] + df_use['nta_count'] > 5]
    print(f'After removing posts with less than or equal to 5 verdicts, there are {str(len(df_use))} posts left')

    # Remove any deleted or removed posts
    gone_list = ['[deleted]', '[removed]', '']
    df_use = df_use[df_use['body'].str.strip().isin(gone_list) == False]
    df_use = df_use.dropna()
    print(f'After removing empty posts, there are {str(len(df_use))} posts left')

    # Sort by timestamp
    df_use = df_use.sort_values(by=['timestamp'])

    return df_use

def main():
    raw = pd.read_csv('1_submission_data_1546300800_1577836800.csv')
    print('Cleaning data')

    clean = clean_data(raw)
    clean.to_csv('aita_clean.csv', index=False, quoting=csv.QUOTE_ALL)

    print('Done')

if __name__ == '__main__':
    main()