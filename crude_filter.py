import os
import pdb
import pandas as pd


def main():
    co_list = os.listdir('data/html')
    finished_cos = []
    for company in co_list:
        finished_cos.append(int(company))

    return finished_cos


if __name__ == "__main__":
    main()
