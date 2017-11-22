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
