from requests_oauthlib import OAuth1Session
import json
import codecs
import schedule
import time
import calendar
from datetime import datetime
import place
import os
i = 1

keys = {
    "CK": "",
    "CS": "",
    "AT": "",
    "AS": "",
}


def mkfile(timeline, place_name):

    for tweet in timeline:
        t = time_change(tweet)
        file_name = t[:16]
        os.chdir(place_name)
        f = codecs.open(file_name + ".json", "w", "utf-8")
        for j in tweet["trends"]:
            json.dump(j, f, indent=2, ensure_ascii=False)
        f.close()


def get_request_twitter(geo):

    sess = OAuth1Session(keys["CK"], keys["CS"], keys["AT"], keys["AS"])

    url = "https://api.twitter.com/1.1/trends/place.json"

    params = {"id": geo}

    request = sess.get(url, params=params)
    return request


def print_rest_request_count(req):
    limit = req.headers['x-rate-limit-remaining']  # リクエスト可能残数の取得
    m = int((int(req.headers['X-Rate-Limit-Reset']) -
             time.mktime(datetime.now().timetuple())) / 60)
    print("リクエスト可能残数: " + limit)
    print('リクエスト可能残数リセットまでの時間:  %s分' % m, "\n")


def main():
    for p, k in place.place.items():
        os.chdir("/home/osamu/Desktop/twitter/tweetdata")
        place_name = p
        geo = k
        os.makedirs(place_name, exist_ok=True)
        request = get_request_twitter(geo)
        if check_valid_api(request):
            timeline = json.loads(request.text)
            mkfile(timeline, place_name)
        else:
            print("Failed: %d" % request.status_code)
    print_rest_request_count(request)
    timeline = json.loads(request.text)
    for tweet in timeline:
        t = time_change(tweet)
    print(t)


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
    schedule.every(10).minutes.do(test)
    while True:
        schedule.run_pending()
        time.sleep(1)
