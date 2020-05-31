import aly_es

import trend_w_search

import t5_w5

import os

import json

import codecs


def main():
    for i in range(13, 15):
        date = "Nov " + str(i)
        print(date)
        gt = aly_es.Analyze_es("東京", "Tokyo", date)
        result = gt.main()
        all_data = trend_w_search.trend_catch(date, result, "Tokyo", "東京")
        t5_w5.save(date, all_data)


def total():
    total_worst = t5_w5.total_w()
    total_top = t5_w5.total_t()

    os.chdir("/home/osamu/Desktop/g-code/anlyze_data")
    f = codecs.open("total_worst" + ".txt", "w", "utf-8")
    f.write(str(total_worst))
    f.close()
    f = codecs.open("total_top" + ".txt", "w", "utf-8")
    f.write(str(total_top))
    f.close()

    print("total_worst", total_worst, "\n")
    print("total_top", total_top)


if __name__ == "__main__":
    main()
    total()
