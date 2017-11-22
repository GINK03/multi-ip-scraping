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

## VMのIPリストを表示する
```console
$ gcloud compute instances list
NAME        ZONE               MACHINE_TYPE   PREEMPTIBLE  INTERNAL_IP  EXTERNAL_IP     STATUS
instance-1  asia-northeast1-b  g1-small                    10.146.0.2                   TERMINATED
my-vm       us-central1-b      n1-standard-1  true         10.128.0.3                   TERMINATED
my-vm0      us-central1-b      n1-standard-1  true         10.128.0.4   35.184.178.159  RUNNING
my-vm1      us-central1-b      n1-standard-1  true         10.128.0.5   104.154.245.47  RUNNING
my-vm2      us-central1-b      n1-standard-1  true         10.128.0.6   104.154.79.77   RUNNING
my-vm3      us-central1-b      n1-standard-1  true         10.128.0.7   35.188.93.220   RUNNING
my-vm4      us-central1-b      n1-standard-1  true         10.128.0.8   35.202.227.110  RUNNING
instance-4  us-central1-c      n1-standard-8               10.128.0.2   35.192.67.51    RUNNING
```
