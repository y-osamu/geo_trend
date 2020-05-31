import os
import codecs
import json
import trend_w_search


total_worst = []
total_top = []


def save(created_at, data):

    ten_count(created_at, data)

    twenty_count(created_at, data)

    os.chdir("/home/osamu/Desktop/g-code/anlyze_data/" +  # ten_countでファイルのパスが生成されている
             created_at[0:3]+"/"+created_at)
    f = codecs.open("alldata" + ".json", "w", "utf-8")
    json.dump(data, f, ensure_ascii=False)
    f.close()

    all_data_result(created_at)


def total_w():
    return total_worst


def total_t():
    return total_top


def ten_count(created_at, data):

    top10 = sorted(data.items(), key=lambda x: x[1], reverse=True)[:10]
    top10 = dict(top10)
    worst10 = sorted(data.items(), key=lambda x: x[1])[:10]
    worst10 = dict(worst10)

    os.chdir("/home/osamu/Desktop/g-code/anlyze_data/" +
             created_at[0:3]+"/"+created_at)
    f = codecs.open("worst10" + ".json", "w", "utf-8")
    json.dump(worst10, f, ensure_ascii=False)
    f.close()

    f = codecs.open("top10" + ".json", "w", "utf-8")
    json.dump(top10, f, ensure_ascii=False)
    f.close()

    total_worst.append(worst10)
    total_top.append(top10)


def twenty_count(created_at, data):

    top20 = sorted(data.items(), key=lambda x: x[1], reverse=True)[:20]
    top20 = dict(top20)
    worst20 = sorted(data.items(), key=lambda x: x[1])[:20]
    worst20 = dict(worst20)

    os.chdir("/home/osamu/Desktop/g-code/anlyze_data/" +
             created_at[0:3]+"/"+created_at)
    f = codecs.open("worst20" + ".json", "w", "utf-8")
    json.dump(worst20, f, ensure_ascii=False)
    f.close()

    f = codecs.open("top20" + ".json", "w", "utf-8")
    json.dump(top20, f, ensure_ascii=False)
    f.close()


def all_data_result(created_at):
    result = trend_w_search.ageru()
    os.chdir("/home/osamu/Desktop/g-code/anlyze_data/" +
             created_at[0:3]+"/"+created_at)
    f = codecs.open("alldata" + ".txt", "w", "utf-8")
    f.write(result)
    f.close()
    print(result)
