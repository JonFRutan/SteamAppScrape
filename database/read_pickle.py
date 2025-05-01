"""Reads a pickled steam data file from the first argument"""

import pickle
from sys import argv
from scrape import printGameData

with open(argv[1], 'rb') as f:
    d = pickle.load(f)
    for i in d:
        printGameData(i)

    print(f"\nNumber of Records: {len(d)}")
    
