# CityGML_conv_height
## 処理概要
* CityGMLファイルを読み込み，bldg:Buildingオブジェクト及びgml:Envelopeの高さ値を変換
    * 相対高さ（地表面をゼロ） -> 標高（JGD2011）
    * 標高 -> 楕円体高（WGS84）

* その他の諸変換
    * gml:id修正： gml:Polygonのgml:idを削除，bldg:Buildingに追加（UUIDベースで生成したランダム値）
    * X/Y反転：WGS84はLon/Lat，JGD2011はLat/Lon

* ファイル出力
    * *_JGD2011フォルダ：標高に変換したCityGMLファイル，srsNameはEPSG:6697(JGD2011)
    * *_WGS84フォルダ：楕円体高に変換したCityGMLファイル，srsNameは"WGS84"

## 利用方法
CityGMLデータが格納されているフォルダに移動し，引数なしでPythonスクリプトを実行
~~~
cd munakata/503054
python CityGML_conv_height.py
~~~
または，引数としてCityGMLデータが格納されているフォルダのパスを指定し，Pythonスクリプトを実行
~~~
python CityGML_conv_height.py munakata/503064
~~~
## 注意事項
* 特定のデータのみでテストしています．データ内容によっては動作しません（例：gml:posのみに対応，座標記述順は決め打ち，，，）．必要に応じて修正してご利用下さい．
* 高さ値の変換処理は，Buildingポリゴンの各座標値について標高及びジオイド高を取得し，その最小値を高さ値に加算する簡易な方法としています．
* 国土地理院のAPIを利用させて頂き，[標高](https://maps.gsi.go.jp/development/elevation_s.html)及び[ジオイド高](https://vldb.gsi.go.jp/sokuchi/surveycalc/api_help.html)を取得しています．API呼び出しは10秒間に10回までと制限があり，1秒毎にAPIをコールしているため，複数プロセスを並行して処理しないよう注意して下さい．また，大量のファイルの処理には時間がかかります．
* 本レポジトリの利用により生じた損失及び損害等について，いかなる責任も負わないものとします．