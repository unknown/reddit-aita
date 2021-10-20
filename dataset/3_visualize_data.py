import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def main():
    random = pd.read_csv('2_aita_random.csv')
    stratified = pd.read_csv('2_aita_stratified.csv')

    plt.hist(
        [random['yta_percent'], stratified['yta_percent']], 
        label=['random', 'stratified']
    )
    plt.legend(loc='upper right')
    plt.show()

if __name__ == '__main__':
    main()