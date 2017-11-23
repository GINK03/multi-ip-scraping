# スクレイピングの際、IPでバンされることを防ぐため、http, httpsの双方に対応したプロキシサーバをGCP プリエンプティかAWS Stop Instanceで構築する
- スクレイピングしていると、どうしても時間あたりのスクレイピング量を最大化しないと業務効率が伸び悩むことがある
- この際、多くのサイトではIPアドレスが連続して同じものでスクレイピングされると、403 Errorを返すサイトがある
- これは規約や業界標準の１秒１スクレイプでも起こることがあり、各社のポリシー感に任せている部分がある
- Global IPをもつAWS StopInstanceやGCP プリエンプティブインスタンスを利用することで、普通のインスタンスより、安価で使い捨てできるプロキシサーバを立てることができる


## GCP プリエンプティブインスタンス
GCPの余剰領域を生かした、24時間限定のインスタンスらしいです。  
時々勝手にシャットダウンされるので、リソースが他で必要な時に奪われているみたいですが、8割ぐらいのコストカットになるということで、安価で使い用によってはとても便利です  

### 手順
1. 通常のインスタンスを立ち上げSquidを設定したイメージを作成しておく
2. Squidが問題なく、プロキシサーバとして機能することを確認したら、イメージをいつでもそのディスクを元にインスタンスを立ち上げるようにできるように設定
3. gcloudコマンドを用い、プリエンプティブインスタンスを購入して、アクセス用のIPを取得

## 前準備：GCPのFirewallに穴を開ける
```
https://cloud.google.com/compute/docs/vpc/using-firewalls?hl=ja
```
<p align="center">
  <img width="750px" src="https://user-images.githubusercontent.com/4949982/33167443-e58369d4-d080-11e7-9098-93a26b179278.png">
</p>

tcp:8080などsquidが使用するポートに穴を開ける

## Squidをインストールして、プロキシサーバとして機能させます
元のユーザ情報やIPがわかってしまうと、意味がないので、x-forwardはOFFでパスワードはかけていないです。（適宜かけてください）
**想定はGCPで起動しているDebian LinuxかUbuntu Linuxです**
**テンプレートファイルをダウンロードします**
```console
$ git clone https://github.com/GINK03/squid-config-dotfile
$ sudo apt install squid
$ cd squid-config-dotfile
$ sudo cp squid.conf.http.anon /etc/squid/squid.conf
$ sudo systemctl restart squid
```
**正常に設定が反映されて、問題なく使用できるかどうか確認します**
```console
$ sudo systemctl status squid
● squid.service - LSB: Squid HTTP Proxy version 3.x
   Loaded: loaded (/etc/init.d/squid; generated; vendor preset: enabled)
   Active: active (running) since Thu 2017-11-23 10:12:00 UTC; 45s ago
```
**クライアントマシンにプロキシを通して、IP確認サイトでステータスを見てみます**
<p align="center">
  <img width="750px" src="https://user-images.githubusercontent.com/4949982/33168050-e7aac908-d082-11e7-94e6-503d5a916273.png">
</p>
<p align="center">
  <img width="750px" src="https://user-images.githubusercontent.com/4949982/33168238-939650b6-d083-11e7-9c71-9b93640bc031.png">
</p>
<div align="center"> 無事、IPが変わることが確認できました </div>


## GCPのマシンのディスクイメージを作成する
GCPのWEB UIより作成が可能です

<p align="center">
  <img width="750px" src="https://user-images.githubusercontent.com/4949982/33168521-915df08c-d084-11e7-9531-68a21fc754cc.png">
</p>
<div align="center"> AWSではAMIの機能に該当するかと思います　　</div>

## プリエンプティブインスタンスを購入する

**gcloudというコマンドがインストールされている必要がります**
```cosnole
$ curl https://sdk.cloud.google.com | bash
```

**試しにmy-vmというインスタンスを立ててみます**  

machine typeはn1-standard-1という最も安価なインスタンスを指定して、インスタンスを作るcompute instances createコマンドの最後に、 **--preemtible**オプションをつけることで、プリエンティブインスタンスとして起動します
```console
$ gcloud compute instances create my-vm --zone us-central1-b --machine-type n1-standard-1 --preemptible
```

## 試しにvmを5台立ち上げてみる
pythonスクリプトでラップアップしておくと楽です
```python
import os                                                       
import sys                                                              
for i in range(5):
  os.system('gcloud compute instances create my-vm{i} --zone us-central1-b --preemptible --image squid-image'.format(i=i)) 
```

## Preemptible VMのIPリストを表示する
JSONフォーマットで受け取るにはこのようにします
```console
$ gcloud compute instances list --format json
```
Pythonで読み取ることで、スクレイパーに渡すIPとマシンネームを紐付けたjsonファイルを生成できます
```python
import json
import os
import re

data = os.popen('gcloud compute instances list --format json').read()
print(data)

name_ip = {}
for data in json.loads( data ):
  if data['scheduling']['preemptible'] != True:
    continue
  if data['status'] != 'RUNNING':
    continue
  try:
    name = data['name']
    print(  data['networkInterfaces'][0] )
    ip = data['networkInterfaces'][0]['accessConfigs'][0]['natIP']
  except KeyError as e:
    continue
  print(name, ip )
  name_ip[name] = ip

open('name_ip.json', 'w').write( json.dumps(name_ip,indent=2) )
```

# (コーディングの例)実際に使ってみる
python3のmultiprocessの機能と、porxyの設定を組み合わせると、ほとんどのサイトの安全システム（一秒間に一回程度にアクセスを抑えるセーフガード）を出し抜くことはできますが、それは使う側の視点としてはコンプライアンスの視点はどうなの？とか、これを行うことによりスクレイピングをするサイトに迷惑をかけてしまい、結果として業務を妨害するようなことになれば、それは業務妨害とか何だと思います  

会社で使うには、スクレイピングするサイトと、法務部とかのチェックや、社内サービスに限定するとか、色々、配慮しなくてはいけない要素は多そうです。  

**exmaple**というディレクトりに、よく使うミニマムなスクレイピングパターンを置いてあります。  
（jin115.comという2chまとめサイトをスクレイピングするように設定されています）  
(requests, bs4というモジュールに依存しています)  
```console
$ cd example
$ python3 jin115.py
```

# AWSでの例
1. AWSインスタンスでsquidがインストールされたAMIを作成する
2. AWS CLIをインストールしてセットアップ
3. spotインスタンスをAWS CLI経由で購入する
4. IP一覧を得る

## 1. AWSインスタンスでsquidがインストールされたAMIを作成する
通常にインスタンスを作成するように、軽めのディスク容量でインスタンスを作成します  
ログインした後、GCPのインスタンスと同じようなプロセスで、squidのインストールとセットアップを行います  
```console
$ ssh -i td2.pem ubuntu@13.230.46.135
[aws instanceログイン後]
$ git clone https://github.com/GINK03/squid-config-dotfile
$ cd squid-config-dotfile
$ sudo apt install squid
$ sudo cp squid.conf.http.anon /etc/squid/squid.conf
$ sudo systemctl restart squid
$ sudo systemctl status squid
● squid.service - LSB: Squid HTTP Proxy version 3.x
   Loaded: loaded (/etc/init.d/squid; bad; vendor preset: enabled)
   Active: active (running) since Thu 2017-11-23 13:48:29 UTC; 28s ago
     Docs: man:systemd-sysv-generator(8)
```
<p align="center">
  <img width="650px" src="https://user-images.githubusercontent.com/4949982/33176086-2632e318-d0a1-11e7-98da-010a1c34a63b.png">
</p>
<div align="center"> AWSの画面からAMIを作成し、このAMIのIDを控えます </div>

## 2. AWS CLIの設定
コマンドライン(CLI)からAWSの機能を扱えるように設定しないと、spot instanceなどをプログラムなどで制御して購入することができません  
**aws cliのインストール**
```console
$ sudo pip3 install awscli
```
**credentialsのセットアップ**
```console
$ cd $HOME
$ mkdir .aws
$ cd .aws
$ cat > credentials
[default]
aws_access_key_id = AKIAIXCQGQV********
aws_secret_access_key = oPOB/24SPrpkq00EIXSAn8X4t********** 
$ aws configure
...
...
Default region name [None]: ap-northeast-1
Default output format [None]: json
```
(Default regionの設定をしくじると、わけのわからないエラーが出ます。一時間溶かしました。。）　

## 3. spotインスタンスをAMIを指定してAWS CLIから購入する
AWSの悪い点として、ドキュメントがとてもわかりにくいので、スクリプトをまとめてラップアップしてテンプレートとしています  

**AWSCLIでは一般的なshellでの記述と、specification.jsonとの両方のファイルが必要です**  
このAMIやkeyNameやSecretGroupIDはお使いのAWS環境に適宜適合させてください
```cosnole
$ cd aws_spot_orders
$ cat spec.json
{
  "ImageId": "ami-9e60d2f8",
  "KeyName": "td2",
  "InstanceType": "m3.medium",
  "SecurityGroupIds": [ "sg-4041b039" ]
}
```
**shellを実行して、インスタンスを起動します**
```console
$ aws ec2 request-spot-instances --spot-price "0.03" --instance-count 1 --type "one-time" --launch-specification file://spec.json
```
より、詳細な設定とオプションは[こちら](http://docs.aws.amazon.com/cli/latest/reference/ec2/request-spot-instances.html)を参照してください。

## 4. SpotインスタンスのIP一覧をAWS CLI経由で得る

