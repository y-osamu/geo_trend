import elasticsearch
import requests
import json
import prefecture
import re
import time
import regex
import prefecture_en


scroll_size = 0
url = "http://geoapi.heartrails.com/api/json?method=searchByGeoLocation"
es = elasticsearch.Elasticsearch("localhost:9200")
res = es.search(scroll="10m", index="twitter", size=10000,
                body={"query": {
                    "bool": {
                        "must": [
                            {"match_phrase": {"created_at": {"query": "Nov 11"}}},
                            # {"bool": {
                            #     "should": [
                            #         {"match_phrase": {
                            #             "place.full_name": {"query": "東京"}}},
                            #         {"match": {
                            #             "place.full_name": {"query": "Tokyo"}}}
                            #     ]
                            # }
                            # }
                        ]}}})
no_pre = no_response = chan_pre = 0
sid = res['_scroll_id']
scroll_size = res['hits']['total']["value"]
print(scroll_size)


def no_prefecture(res):
    global no_pre, no_response, chan_pre

    for i in res["hits"]["hits"]:
        # print(i["_source"]["place"]["full_name"])
        if pre_name(i["_source"]["place"]["full_name"]) == 0:
            no_pre += 1
            # lon 東経　lat 北緯
            lon = i["_source"]["place"]["point"][0]
            lat = i["_source"]["place"]["point"][1]
            param = {
                "method": "searchByGeoLocation",
                'x': lon,
                'y': lat
            }
            response = requests.get(url, params=param)
            jsonData = response.json()

            if "location" not in jsonData["response"].keys():
                no_response += 1
                # es.delete(index="twitter", doc_type="_doc", id=i["_id"])
                print(i["_id"], "のデータを削除しました")

            else:
                # es.update(index="twitter", doc_type="_doc", id=i["_id"], body={"doc": {"place": {
                      # "full_name": jsonData["response"]["location"][0]["prefecture"] + jsonData["response"]["location"][0]["city"]}}})
                print(i["_id"], "の[place][full_name]=", i["_source"]["place"]["full_name"], "を→ ", jsonData["response"]["location"][0]["prefecture"] +
                      jsonData["response"]["location"][0]["city"], "に変えました")
                chan_pre += 1


def timeprint(execution_time):
    m = s = t = d = 0
    if execution_time >= 60:
        m, s = divmod(execution_time, 60)
        print(m, "分", s, "秒")

        if m >= 60:
            t, m = divmod(m, 60)
            print(t, "時間", m, "分", s, "秒")
            if t >= 24:
                d, t = divmod(t, 24)
                print(d, "日", t, "時間", m, "分", s, "秒")
    else:
        s = execution_time
        print(s, "秒")


def pre_name(fullname):
    match = re.match('[a-zA-Z]', fullname)
    h = 0

    if match == None:
        for k in prefecture.place:
            if k in fullname:
                h += 1
        if h != 0:
            h = 0
        else:
            if fullname == "日本":
                print(fullname)
            return 0
    else:
        for k in prefecture_en.place:
            if k in fullname:
                h += 1
        if h != 0:
            h = 0
        else:
            if fullname == "Japan":
                print(fullname)
            return 0


j = 0

total_time = time.perf_counter()
no_prefecture(res)

while (scroll_size > 0):
    start_time = time.perf_counter()
    print("Scrolling...")
    res = es.scroll(scroll_id=sid, scroll='10m')
    no_prefecture(res)
    # Update the scroll ID
    sid = res['_scroll_id']
    # Get the number of results that we returned in the last scroll
    scroll_size = len(res['hits']['hits'])
    execution_time = time.perf_counter() - start_time
    timeprint(execution_time)
    # print("scroll size: " + str(scroll_size))
    j += 1
    print("\n"*3, j, "回目")

total_time2 = time.perf_counter() - total_time


print(j, "回", "県情報なしデータ", no_pre, "seaデータ", no_response, "県情報追加データ", chan_pre)
timeprint(total_time2)
