# 自動CTデータ ダウンロードプログラム

- [インストール方法](#インストール方法)
- [基本の使い方](#基本の使い方)
- [応用（便利な使い方）](#応用（便利な使い方）)
- [更新履歴](#更新履歴)



## インストール方法
- ご自身のPCで使う場合は，まずpythonおよびrequestsモジュールのインストールが必要です．手順は[こちら](#pythonのインストール) ．SPring-8データセンターではこの作業は不要．
- [ここ](https://github.com/xrm-bl/aCT-download/archive/refs/heads/main.zip)からプログラムをダウンロードする．
- zipファイルを展開して，`actinfo.py`と`actget.py`をわかりやすい場所に置く．
    - データセンターの場合は，OpenOndemandのFilesからホームディレクトリ(`/home/ユーザーID/`)にアップロードするのがわかりやすい．

## 基本の使い方
### 課題番号内のデータ一覧を表示する: actinfo.py
- `python3 actinfo.py --user ユーザーID --proposal 課題番号`
- パスワードを入力する．
- サンプル番号と測定メタデータ一覧表が表示される．　　　　
- 例
```
[j00XXXXX@fep4 ]$ python3 actinfo.py --user j00XXXXX --proposal 2024AXXXX


Password: 


2024AXXXX Searching...
X data found
+-----------------------------------------------------------------------------------------------------------------+
| Sample ID        | Sample Name      | Pixel Size       | Exposure         | Projections      | X-ray            |
+------------------+------------------+------------------+------------------+------------------+------------------+
| XXXXXXXXXX       | XXXXX            | X.XX um/pixel    | XXX.X ms         | XXXX             | XXX keV          |
| XXXXXXXXXX       | XXXXX            | X.XX um/pixel    | XXX.X ms         | XXXX             | XXX keV          |
+-----------------------------------------------------------------------------------------------------------------+
```

### サンプル名を指定してデータをダウンロードする: actget.py
- `python3 actget.py --user ユーザーID --proposal 課題番号 --sampleid サンプル番号 --zip ダウンロードするデータの種類(ro/ro_222/ro_444/rh/rh_222/rh_444)`
- パスワードを入力する．
- データセンターでは/UserData/ユーザーid配下，ローカルPCではカレントディレクトリに課題番号とサンプル番号のディレクトリが自動作成されて，zipファイルがダウンロードされる．
- zipファイルはダウンロードされた後，自動的に展開される．zipファイルは削除される．　　
- 例
```
[j00XXXXX@fep4 ]$ python3 actget.py --user j00XXXXX --proposal 2024AXXXX --sampleid XXXXXXXXX --zip ro_444


Password: 

Zip will be donwloaded to /UserData/j00XXXXX
Smaller zip (4x4x4 and ro) will be first served. PRESS Ctrl + C for cancel


Downloading: https://dc-act.spring8.or.jp/remote.php/dav/files/j00XXXXX/2024AXXXX/XXXXXXXXXX/ro_444.zip
zip downloaded successfully!: /UserData/j00XXXXX/2024AXXXX/XXXXXXXXXX/ro_444.zip (2 sec. elapsed, speed = 524 MB/sec)
Extracting... 100.00%
Extraction complete. (17 sec.)
```

## 応用
- コマンド操作に慣れた方むけの，便利なオプション
### actinfo.py
- `--samplename` `--pixelsize` `--exposure` `--projections` `--xray`で，サンプル名/画素サイズ/露光時間/投影数/Ｘ線エネルギーで絞込検索ができる．単位は不要．各条件につき入力値は1個まで．複数条件を使用した場合はAND検索として実行される．    
- `--csv`をつけると，表をcsvファイルとして保存できる．

### actget.py
- `--output`で任意の保存先パスを指定可能．
- `--sampleid`は複数指定可能．
- `--sampleid`を付けない場合は，課題番号内の全てのサンブル番号のデータをダウンロードする．
- `--zip`では複数種類を指定可能．複数指定した場合は，サイズの軽いもの（roおよび4x4x4ビニングデータ）を優先して処理する．
- `--zip all` `--zip allro` `--zip allrh` `--zip all222` `--zip all444`という指定も可能．
- `--nounzip`をつけると，zipファイルのダウンロードのみで，展開を行わない．

## pythonのインストール
- python 3.xとrequestsモジュールが必要です．
- linuxでは
```
sudo apt -y update
sudo apt -y upgrade
sudo apt install python3 python3-pip -y
sudo pip3 install pip -U
pip install requests
```
- windowsでは，https://www.python.jp/install/windows/install.html に従ってpythonをインストール後
```
pip install requests
```
- MacOSでは，python3がプリインストールされているはずですので，requestsモジュールをインストールします．
```
pip3 install requests
```

## 更新履歴
- 2024/5/23 actinfo.py: 転送途中のサンプル番号がある場合の読み取りエラーを回避． 
