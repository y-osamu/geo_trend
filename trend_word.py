from requests_oauthlib import OAuth1Session
import json
import codecs
import schedule
import time
import calendar
from datetime import datetime
# import place
import os

keys = {
    "CK": "",
    "CS": "",
    "AT": "",
    "AS": "",
}


def trend(file_name, tweet):
    mydict = {}
    os.chdir(file_name)
    f = codecs.open(file_name + ".json", "w", "utf-8")
    for j in tweet:
        json.dump(j, f, indent=2, ensure_ascii=False)
        mydict1 = {j["name"]: j["tweet_volume"]}
        mydict.update(mydict1)
    f.close()
    return mydict


def mkfile(timeline, place_name):

    for tweet in timeline:
        t = time_change(tweet)
        file_name = t[:16]
        os.makedirs(file_name, exist_ok=True)
        s = trend(file_name, tweet["trends"])

    return s, file_name


def request_twitter(geo, url):

    sess = OAuth1Session(keys["CK"], keys["CS"], keys["AT"], keys["AS"])

    params = {"id": geo}

    request = sess.get(url, params=params)
    return request


def print_rest_request_count(req, s):
    limit = req.headers['x-rate-limit-remaining']  # リクエスト可能残数の取得
    m = int((int(req.headers['X-Rate-Limit-Reset']) -
             time.mktime(datetime.now().timetuple())) / 60)
    print(s + "\n" + "リクエスト可能残数: " + limit)
    print('リクエスト可能残数リセットまでの時間:  %s分' % m, "\n")


def main():
    t = "trend"
    trend = "https://api.twitter.com/1.1/trends/place.json"
    place_name = "tokyo"
    geo = 1118370

    os.chdir("/home/osamu/Desktop/try/tokyo")

    trend_request = request_twitter(geo, trend)

    print_rest_request_count(trend_request, t)

    if check_valid_api(trend_request):
        timeline = json.loads(trend_request.text)
        s = mkfile(timeline, place_name)
    else:
        print("Failed: %d" % trend_request.status_code)
    return s


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


if __name__ == '__main__':
    main()
