from requests_oauthlib import OAuth1Session
import json
import codecs
import schedule
import time
import calendar
from datetime import datetime
import trend_word
import os
i = 1

keys = {
    "CK": "",
    "CS": "",
    "AT": "",
    "AS": "",
}


def trend(file_name, tweet):
    s = []
    f = codecs.open(file_name + ".json", "w", "utf-8")
    for j in tweet:
        json.dump(j, f, indent=2, ensure_ascii=False)
        s.append(j["name"])
    f.close()

    return s


def mkfile(timeline, place_name):

    for tweet in timeline:
        t = time_change(tweet)
        file_name = t[:16]
        # os.chdir(place_name)
        s = trend(file_name, tweet["trends"])

    return s


def request_twitter(trend_word):

    url = "https://api.twitter.com/1.1/search/tweets.json"

    sess = OAuth1Session(keys["CK"], keys["CS"], keys["AT"], keys["AS"])

    params = {"q": trend_word,
              "count": 100}

    request = sess.get(url, params=params)
    return request


def print_rest_request_count(req, s):
    print(req.headers['x-rate-limit-remaining'])
    limit = req.headers['x-rate-limit-remaining']  # リクエスト可能残数の取得
    m = int((int(req.headers['X-Rate-Limit-Reset']) -
             time.mktime(datetime.now().timetuple())) / 60)
    print(s + "\n" + "リクエスト可能残数: " + limit)
    print('リクエスト可能残数リセットまでの時間:  %s分' % m, "\n")


def main():
    t = "けんさく"
    t_word = trend_word.main()
    trend_time = t_word[1]
    trend_w = t_word[0]
    os.chdir("/home/osamu/Desktop/try/tokyo/"+trend_time)
    f = codecs.open(trend_time + ".txt", "w", "utf-8")
    for k, v in trend_w.items():
        print(k, v)
        trend_request = request_twitter(k)
        f.write("\n" + "-"*100 + "\n")
        w = "【{0}】{1}".format(k, v)
        f.write(w)
        if check_valid_api(trend_request):
            timeline = json.loads(trend_request.text)
            for tweet in timeline["statuses"]:
                string = "\n\n{0}\n\n".format(tweet["text"])
                f.write(string)
        else:
            print("Failed: %d" % trend_request.status_code)
    f.close()
    print_rest_request_count(trend_request, t)


def check_valid_api(req):
    if req.status_code == 200:
        return True
    else:
        return False


def time_change(tweet):
    time_utc = time.strptime(tweet['created_at'], '%Y-%m-%dT%H:%M:%SZ')
    unix_time = calendar.timegm(time_utc)
    time_local = time.localtime(unix_time)
    japan_time = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    return japan_time


def test():
    global i
    i += 1
    print(str(i) + "回目")
    return main()


if __name__ == '__main__':
    main()
    schedule.every(15).minutes.do(test)
    while True:
        schedule.run_pending()
        time.sleep(1)
