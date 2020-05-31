import elasticsearch

import MeCab

import json

import os

import codecs

haiki = []
tukau = []
es = elasticsearch.Elasticsearch("localhost:9200")
all_data = {}


def trend_catch(created_at, result, e_name, j_name):

    for i in result:
        tokyo_total = kibana_tokyo(i, created_at, e_name, j_name)
        if tokyo_total != None:
            total = kibana_total(i, created_at)
            ration = round(tokyo_total/total, 4)
            detail(created_at, i, total, tokyo_total, ration)
            sub_data = {i[0]: ration}
            all_data.update(sub_data)
    # print(all_data)
    # print("使用単語", "\n", tukau)
    # print("不使用単語", "\n", haiki)

    return all_data


def kibana_tokyo(i, created_at, e_name, j_name):
    body = {"query": {"bool": {"must": [
        {"bool": {"must": [{"match_phrase": {"created_at": {"query": created_at}}},
                           {"match_phrase": {
                               "text": {"query": i[0]}}}
                           ]}},
        {"bool": {"should": [{"match_phrase": {"place.full_name": {"query": e_name}}},
                             {"match_phrase": {
                                 "place.full_name": {"query": j_name}}}
                             ]}
         }]}}}

    res = es.search(index="twitter", size=10000, body=body)

    #print(i[0], "kibana", res['hits']['total']["value"], "mecab", i[1])

    if res['hits']['total']["value"] < i[1]:
        if abs(res['hits']['total']["value"] - i[1]) > 20 and res['hits']['total']["value"] < 70:
            haiki.append(i[0])
            haiki.append(i[1])
            haiki.append(res['hits']['total']["value"])

        else:
            tukau.append(i[0])
            tukau.append(res['hits']['total']["value"])
            return res['hits']['total']["value"]
    else:
        tukau.append(i[0])
        tukau.append(res['hits']['total']["value"])
        return res['hits']['total']["value"]


def kibana_total(i, created_at):
    body = {"query": {"bool":  {"must": [{"match_phrase": {"created_at": {"query": created_at}}},
                                         {"match_phrase": {"text": {"query": i[0]}}}]
                                }}}

    res = es.search(index="twitter", size=10000, body=body)
    tukau.append(res['hits']['total']["value"])

    return res['hits']['total']["value"]


def ageru():
    return "使用[単語,mecab,kibana]\n{0}\n\n未使用\n{1}\n\n割合\n{2}\n\n".format(tukau, haiki, all_data)


def detail(created_at, i, total, tokyo_total, ration):

    os.chdir("/home/osamu/Desktop/g-code/anlyze_data")
    os.makedirs(created_at[0:3], exist_ok=True)  # make Month three letter file

    os.chdir("/home/osamu/Desktop/g-code/anlyze_data/" + created_at[0:3])
    os.makedirs(created_at, exist_ok=True)  # make day file

    os.chdir("/home/osamu/Desktop/g-code/anlyze_data/" +
             created_at[0:3]+"/"+created_at)
    string = "【{0}】 の総ツイート数{1}  東京のツイート数{2} 割合{3}".format(
        i[0], total, tokyo_total, ration)
    f = codecs.open("ration_detail.txt", "w", "utf-8")
    f.write(string)
    f.close()
