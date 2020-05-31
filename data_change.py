import elasticsearch
import requests
import json
import prefecture
import prefecture_en
import re
import time
import regex
import notice_send


class Data_fix():
    no_pre = 0  # 県名がないカウント数
    no_response = 0  # 県名変更の際にレスポンスの無い数
    change_pre = 0  # 変更されたツイート数
    es = elasticsearch.Elasticsearch("localhost:9200")
    total_tweet_volume = 0
    japan = 0
    # インスタンス変数として扱うと、オブジェクトごとに値をとれる

    def __init__(self, search_date):
        self.scroll_size = 0  # ページングのページ数
        self.sid = 0  # スクロールID
        self.scroll_size = 0  # スクロールするサイズ
        self.res = None  # esのレスポンス
        self.search_date = search_date  # 日付

    def es_connect(self):
        body = {"query": {"match_phrase": {"created_at": self.search_date}}}
        self.res = self.es.search(scroll="10m", index="twitter",
                                  size=10000, body=body)
        self.sid = self.res['_scroll_id']
        self.scroll_size = self.res['hits']['total']["value"]
        self.total_tweet_volume = self.scroll_size

    def no_prefecture(self):
        for i in self.res["hits"]["hits"]:
            if self.pre_name(i) == 0:
                self.no_pre += 1
                geo = self.geo_req(i["_source"]["place"]["point"])
                if "location" not in geo["response"].keys():
                    self.no_response += 1
                    self.es.delete(index="twitter",
                                   doc_type="_doc", id=i["_id"])
                    print(i["_source"]["place"]["full_name"],
                          i["_id"], "のデータを削除しました", i["_source"]["place"]["point"], "\n"*3)

                else:
                    self.es.update(index="twitter", doc_type="_doc", id=i["_id"], body={"doc": {"place": {
                        "full_name": geo["response"]["location"][0]["prefecture"] + geo["response"]["location"][0]["city"]}}})
                    print(i["_id"], "の[place][full_name]=", i["_source"]["place"]["full_name"], "を→ ",
                          geo["response"]["location"][0]["prefecture"] +
                          geo["response"]["location"][0]["city"], "に変えました")
                    self.change_pre += 1

    def pre_name(self, i):
        match = re.match('[a-zA-Z]', i["_source"]["place"]["full_name"])
        h = 0

        if match == None:
            for k in prefecture.place:
                if k in i["_source"]["place"]["full_name"]:
                    h += 1
            if h != 0:
                h = 0
            else:
                if i["_source"]["place"]["full_name"] == "日本":
                    self.es.delete(index="twitter",
                                   doc_type="_doc", id=i["_id"])
                    print(i["_source"]["place"]["full_name"],
                          i["_id"], "のデータを削除しました", i["_source"]["place"]["point"])
                    self.japan += 1
                else:
                    return 0
        else:
            for k in prefecture_en.place:
                if k in i["_source"]["place"]["full_name"]:
                    h += 1
            if h != 0:
                h = 0
            else:
                if i["_source"]["place"]["full_name"] == "Japan":
                    self.es.delete(index="twitter",
                                   doc_type="_doc", id=i["_id"])
                    print(i["_source"]["place"]["full_name"],
                          i["_id"], "のデータを削除しました", i["_source"]["place"]["point"])
                    self.japan += 1

                else:
                    return 0

    def geo_req(self, point):
        geourl = "http://geoapi.heartrails.com/api/json?method=searchByGeoLocation"
        # lon 東経　lat 北緯
        lon = point[0]
        lat = point[1]
        param = {
            "method": "searchByGeoLocation",
            'x': lon,
            'y': lat
        }
        response = requests.get(geourl, params=param)
        jsonData = response.json()
        return jsonData

    def timeprint(self, execution_time):
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

    def main(self):
        j = 2
        total_time = time.perf_counter()
        self.es_connect()
        self.no_prefecture()

        while (self.scroll_size > 0):
            print("\n"*3, j, "回目")
            start_time = time.perf_counter()
            print("Scrolling...")
            self.res = self.es.scroll(scroll_id=self.sid, scroll='10m')
            self.no_prefecture()
            self.sid = self.res['_scroll_id']  # Update the scroll ID
            self.scroll_size = len(self.res['hits']['hits'])
            execution_time = time.perf_counter() - start_time
            self.timeprint(execution_time)
            j += 1

        total_time2 = time.perf_counter() - total_time
        print(j, "回")
        print("【", self.search_date, "】の総ツイート数", self.total_tweet_volume, "県情報なしデータ", self.no_pre, "seaデータ",
              self.no_response, "日本のみ", self.japan, "県情報追加データ", self.change_pre)
        print("新たな総ツイート数", self.total_tweet_volume-self.no_response-self.japan)
        self.timeprint(total_time2)


for i in range(1, 32):
    i = '%02d' % i
    datestring = "Oct"+" "+str(i)
    print(datestring)
    s = Data_fix(datestring)

    try:
        notice_send.send_slack_log(datestring+"のデータ投入中")
        s.main()
        notice_send.send_slack_log(datestring+"終了")

    except:
        import traceback
        print(traceback.format_exc())
        notice_send.send_slack_log(
            "エラーが発生しました。３秒後にもう一度挑戦します" + traceback.format_exc())

        try:
            time.sleep(3)
            notice_send.send_slack_log(datestring+"のデータ投入中")
            s.main()
            notice_send.send_slack_log(datestring+"終了")
        except:
            print(traceback.format_exc())
            notice_send.send_slack_log(
                "エラーが発生しました" + traceback.format_exc())


notice_send.send_slack_log("全部おわり！")
