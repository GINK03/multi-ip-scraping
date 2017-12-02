import requests

import concurrent.futures

import bs4

import json

import os

import random

import sys

import gzip

import pickle
proxies = []
for name_ip in open('../aws_ip.txt'):
  name, ip = name_ip.strip().split()
  proxies.append( {'http':'{}:8080'.format(ip), 'https':'{}:8080'.format(ip) } )


def url_fix(url_, urls):
  furls = set()
  for url in urls:
    try:
      if url[0] == '/':
        top = url_.split('/')[2]
        url = 'http://' + top + '/' + url
        furls.add(url)
        continue
    except Exception:
      continue
    if 'javascript' in url:
      continue
    if 'kakaku.com' not in url:
      continue
    furls.add(url)
  return furls

def map1(arr):
  index, url = arr
  save_name = 'htmls/' + url.replace('/', '_')
  if os.path.exists(save_name) is True:
    return set()
  print( 'now url', url ) 
  try:
    r = requests.get(url, proxies=proxies[index%len(proxies)])
    r.encoding = r.apparent_encoding
  except Exception as ex:
    print(ex)
    return set()
  html = r.text
  try:
    open( save_name, 'w' ).write( html )  
  except OSError:
    return set()
  soup = bs4.BeautifulSoup(r.text, "html5lib")
  urls = set()
  for a in soup.find_all('a', href=True):
    _url = a['href']
    urls.add(_url)
  #print('a', urls)
  save_link_name = 'links/' + url.replace('/', '_')
  url_ret = url_fix(url, urls)
  open(save_link_name, 'w').write( json.dumps(list(url_ret), indent=2, ensure_ascii=False) )
  return url_ret

urls = {'http://bbs.kakaku.com/bbs/K0000565942/SortID=21194172/'}
if '--resume' in sys.argv:
  urls = pickle.loads(gzip.decompress(open('urls.pkl.gz', 'rb').read()))

while True:
  arrs = [(index,url) for index,url in enumerate(urls)]
  
  nexts = set()
  with concurrent.futures.ProcessPoolExecutor(max_workers=1*len(proxies)) as exe:
    for urls in exe.map(map1, arrs):
      for url in urls:
        nexts.add(url)
  #for arr in arrs:
  #  for url in map1(arr):
  #    nexts.add(url) 
  print(nexts)
  urls = nexts
