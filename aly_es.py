import elasticsearch

import MeCab

import json

import collections

import re

import spam

total = 0


class Analyze_es:
    def __init__(self, j_name, p_name, created_at):
        self.j_name = j_name
        self.p_name = p_name
        self.created_at = created_at
        self.sid = None
        self.scroll_size = 0
        self.res = None
        self.es = elasticsearch.Elasticsearch("localhost:9200")
        self.count = 0
        self.data = None
        self.result = []

    def get_es(self):
        self.res = self.es.search(scroll="2m", index="twitter", size=10000,
                                  body={"query": {
                                      "bool": {
                                          "must": [
                                              {"match_phrase": {"created_at": {
                                                  "query": self.created_at}}},
                                              {"bool": {
                                                  "should": [
                                                      {"match_phrase": {
                                                          "place.full_name": {"query": self.p_name}}},
                                                      {"match_phrase": {
                                                          "place.full_name": {"query": self.j_name}}}
                                                  ]
                                              }
                                              }]}}})
        self.sid = self.res['_scroll_id']
        self.scroll_size = self.res['hits']['total']["value"]
        self.get_data()

    def get_data(self):
        for i in self.res["hits"]["hits"]:
            self.data_trim(i["_source"]["text"])
            self.cab_separate()
            self.count += 1

    def scroll(self):
        global total
        total = self.scroll_size
        while (self.scroll_size > 0):
            print("Scrolling...")
            self.res = self.es.scroll(scroll_id=self.sid, scroll='2m')
            # print(self.res["hits"]["hits"])
            self.get_data()
            # Update the scroll ID
            self.sid = self.res['_scroll_id']
           # Get the number of results that we returned in the last scroll
            self.scroll_size = len(self.res['hits']['hits'])
            print("scroll size: " + str(self.scroll_size))

    def cab_separate(self):
        tagger = MeCab.Tagger(
            "-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd")
        tagger.parse("")
        node = tagger.parseToNode(self.data)
        result2 = []

        while node:
            hinshi = node.feature.split(",")[0]
            if hinshi == '名詞':
                if node.feature.split(",")[6] in spam.spam:
                    pass
                else:
                    if node.feature.split(",")[1] == "固有名詞":
                        if node.feature.split(",")[2] != "地域":
                            m = re.search(r"(^[a-zA-Z0-9]+$|[!-/:-@[-`{-~]|[Α-ω])",
                                          node.feature.split(",")[6])
                            if m != None:
                                pass
                            else:
                                if node.feature.split(",")[6] not in result2:
                                    result2.append(node.feature.split(",")[6])
                                    self.result.append(
                                        node.feature.split(",")[6])

            node = node.next

    def data_trim(self, text):
        ryaku = "(@[a-zA-Z0-9_]+\s|https?://[\w/:%#\$&\?\(\)~\.=\+\-]+)"
        self.data = re.sub(ryaku, "", text)

    def main(self):
        global total
        self.get_es()
        self.scroll()
        c = collections.Counter(self.result)
        print("場所", self.j_name, "ツイート数", total, "日付", self.created_at,
              "全単語数", len(self.result), "\n")
        result = c.most_common(50)

        return result

    def save_data(self):
        return print("場所", self.j_name, "ツイート数", total, "日付", self.created_at, "全単語数", len(self.result), "\n")
