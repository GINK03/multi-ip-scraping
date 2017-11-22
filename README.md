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
