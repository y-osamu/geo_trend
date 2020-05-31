import glob

import codecs

import elasticsearch

import json

import time

import notice_send


def main():
    start_time = time.perf_counter()
    dataset()
    execution_time = time.perf_counter() - start_time
    timeprint(execution_time)


def timeprint(execution_time):
    m = s = t = d = 0
    if execution_time >= 60:
        m, s = divmod(execution_time, 60)
        if m >= 60:
            t, m = divmod(m, 60)
            print(t, "時間", m, "分", s, "秒")
            if t >= 24:
                d, t = divmod(t, 24)
                print(d, "日", t, "時間", m, "分", s, "秒")
    else:
        s = execution_time
        print(s, "秒")


def initilize(dic):

    # dpbc[0][0]=一つひとつの位置座標　dpbc[0][0][0]= 経度　dpbc[0][0][1]= 緯度　書き方の省略
    if dic["place"]["bounding_box"] == None:
        return None
    else:
        dpbc = dic["place"]["bounding_box"]["coordinates"]

        # ５つめの位置情報の追加
        dpbc[0].append(dpbc[0][0])

        # ------------------------------------ここから下のでーたはよび-----------------------------
        # リストの文字を小文字に変換する
        dic["place"]["bounding_box"]["type"] = dic["place"]["bounding_box"]["type"].lower()

        # 書き方の省略 データタイプがどうなっているか？
        dpbt = dic["place"]["bounding_box"]["type"]

        # -------------------------------------------------------------------------------------------
        return dpbc, dpbt


def make_dic(dic):
    # 辞書の統合
    doc = {"place": dic["place"]}
    text = {"text": dic["text"]}
    time_at = {"created_at": dic["created_at"]}
    doc.update(text)
    doc.update(time_at)
    # 必要になったら追加する
    # source = {"source": dic["source"]}
    # source.update(dic["user"])
    # doc.update(source)
    # print(doc)
    return doc


def dataset():
    path_list = glob.glob('/home/osamu/Desktop/twitter/tweetdata/*')
    path_list.sort()

    for directory in path_list:

        a = glob.glob(directory + "/*")
        a.sort()

        start = time.perf_counter()

        print(directory + "投入中")

        for dpath in a:

            notice_send.send_slack_log(dpath + "のデータ投入中")

            with open(dpath, encoding="utf-8") as f:

                line = f.readline()

                while line:
                    # for i in range(1000):
                    li = line[20:]
                    dic = json.loads(li)

                    # dic["place"]に値が入ってない場合　
                    if dic["place"] == None:
                        pass
                    else:
                        dpbc = initilize(dic)

                        if dpbc == None:
                            pass
                        else:
                            dpbc = dpbc[0]
                            # そのデータが日本かどうか？
                            if dic["place"]["country_code"] == "JP":
                                # lat = 緯度 lon = 経度
                                la = (dpbc[0][0][1] + dpbc[0][1][1])/2
                                lo = (dpbc[0][0][0] + dpbc[0][3][0])/2
                                lat = round(la, 6)
                                lon = round(lo, 6)
                                dic["place"]["point"] = [lon, lat]
                                dic = make_dic(dic)
                                print(dic)
                                # client = elasticsearch.Elasticsearch(
                                #     "localhost:9200")
                                # client.index(index='twitter',
                                #              doc_type='_doc', body=dic)
                    line = f.readline()
        notice_send.send_slack_log(directory + "のデータが投入されました")
        print(directory+"のデータが投入されました")
        execution = time.perf_counter() - start
        timeprint(execution)


if __name__ == '__main__':
    try:
        main()
    except:
        import traceback
        print(traceback.format_exc())
        notice_send.send_slack_log("エラーが発生しました" + traceback.format_exc())
