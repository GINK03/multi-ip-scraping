# GCP

## GCPのFirewallに穴を開ける
```
https://cloud.google.com/compute/docs/vpc/using-firewalls?hl=ja
```
から、tcp:8080などsquidが使用するサーバに穴を開ける

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
