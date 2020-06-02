**Elasticsearchを使用したTweet情報からのトレンド抽出と可視化**

index.py   
ES にデータを投入するための“マッピング“ファイル. データベースでいうテーブル等のスキーマの定義みたいなもん. スキーマレスなストレージ機能があるが,データ型が既に決まっている場合,定義した方が 良い. 地図上に表示させる機能を使う場合,緯度経度のタイプが必要等,ES 側でタイプの取 り決めがあるため,公式サイトの方で確認した方が良い._doc の中の Key は自由に設定可能,本研究の場合,place.properties.point という Key で geo_point(ES 指定の型)というタイプでデータが投入されている.Settinng の Analyzer で kuromoji とあるが日本語形態素解析のツールである.2020 年 2 月 26 日時点で,上位互換となる解析ツールもある模様.

snowv.py (名前の由来, 冬休み中にデータ投入を行なったため,SnowVacationから命名)   
先生から頂いた Tweet データを形成しなおし E S に投入する
日本のデータかどうか確認→必要なデータだけを辞書型に再構成→投入
Polygon 型のデータは,緯度経度情報をもう一つ追加しないと ES に投入できないため,緯度 経度を追加している.Polygon 型のデータは point 型に変更している.
Slack に投入通知を流している

notice_send.py  
Slack に通知させるためのファイル.

data_change.py  
県情報がないデータを A P I によって書き換えるファイル.


prefecture.py prefecture_en.py  
県情報の有無の確認の際,47 都道府県のリストデータを作り確認するためのファイル. prefecture_en の方は,47 都道府県名の英語バージョン.


spam.py  
Mecab 解析の際に弾く Spam となる単語


all_graduation.py  
以下の 3 つのファイルを実行するファイル 
・aly_es.py
・trend_w_search.py
・t5_w5.py


aly_es.py   
ES からツイートデータを取ってきて,Mecab によって形態素解析を行い, 固有名詞を抽出.  
trend_w_search.py   
使用する単語を抽出,割合計算
t5_w5.py  
上位 10,20,下位 10,20 この単語抽出,ファイルに保存



