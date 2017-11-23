# スクレイピングの際、IPでバンされることを防ぐため、http, httpsの双方に対応したプロキシサーバをGCP プリエンプティかAWS Stop Instanceで構築する
- スクレイピングしていると、どうしても時間あたりのスクレイピング量を最大化しないと業務効率が伸び悩むことがある
- この際、多くのサイトではIPアドレスが連続して同じものでスクレイピングされると、403 Errorを返すサイトがある
- これは規約や業界標準の１秒１スクレイプでも起こることがあり、各社のポリシー感に任せている部分がある
- Global IPをもつAWS StopInstanceやGCP プリエンプティブインスタンスを利用することで、普通のインスタンスより、安価な使い捨てプロキシサーバを立てることができる


## GCP プリエンプティブインスタンス

### 手順
1. 通常のインスタンスを立ち上げSquidを設定したイメージを作成しておく
2. Squidが問題なく、プロキシサーバとして機能することを確認したら、イメージをいつでもそのディスクを元にインスタンスを立ち上げるようにできるように設定
3. gcloudコマンドを用い、プリエンプティブインスタンスを購入して、アクセス用のIPを取得

## 前準備：GCPのFirewallに穴を開ける
```
https://cloud.google.com/compute/docs/vpc/using-firewalls?hl=ja
```
から、tcp:8080などsquidが使用するサーバに穴を開ける

## 

## プリエンプティブインスタンスを購入する

```console
$ gcloud compute instances create my-vm --zone us-central1-b --preemptible
```

## Squidをインストールしてちゃんとプロキシサーバとして機能することを確認する
```console
$ sudo apt install git squid tmux vim
$ git clone https://github.com/GINK03/squid-config-dotfile
$ cd squid-config-dotfile
$ sudo cp {$TARGET_FILE} /etc/squid.conf
$ sudo systemctl restart squid
$ sudo systemctl status squid
```
可能ならば、クライアントマシンで動作を確認する

## GCPのマシンのディスクイメージを作成する
web UIからログインして対応する

Instances... -> Create Image

## 試しにvmを5台立ち上げてみる
pythonスクリプトでラップアップ
```python
import os                                                       
import sys                                                              
for i in range(5):
  os.system('gcloud compute instances create my-vm{i} --zone us-central1-b --preemptible --image squid-image'.format(i=i)) 
```

## VMのIPリストを表示する
```console
$ gcloud compute instances list --format json
```
```python
import json
import os
import re

data = os.popen('gcloud compute instances list --format json').read()
print(data)

for data in json.loads( data ):
  if data['scheduling']['preemptible'] != True:
    continue
  if data['status'] != 'RUNNING':
    continue
  try:
    name = data['name']
    ip = data['networkInterfaces'][0]['networkIP']
  except KeyError as e:
    continue
  print(name, ip )
```
