import requests

import concurrent.futures

import bs4

import json

import os

import random
name_ip = json.loads( open('../gcp_name_ip.json').read() )
proxies = []
for name, ip in name_ip.items():
  proxies.append( {'http':'{}:8080'.format(ip), 'https':'{}:8080'.format(ip) } )


def url_fix(urls):
  furls = set()
  for url in urls:
    try:
      if url[0] == '/':
        url = 'http://jin115.com/' + url
        furls.add(url)
        continue
    except Exception:
      continue
    if 'javascript' in url:
      continue
    if 'http://jin115.com/' not in url:
      continue
    furls.add(url)
  return furls

def map1(arr):
  index, url = arr
  save_name = 'htmls/' + url.replace('/', '_')
  if os.path.exists(save_name) is True:
    return set()
  print( 'now url', url ) 
  r = requests.get(url, proxies=proxies[index%len(proxies)])
  html = r.text
  open( save_name, 'w' ).write( html )  
  soup = bs4.BeautifulSoup(r.text)
  urls = set()
  for a in soup.find_all('a', href=True):
    url = a['href']
    urls.add(url)
  #print('a', urls)
  return url_fix(urls)

urls = {'http://jin115.com/'}

while True:
  arrs = [(index,url) for index,url in enumerate(urls)]
  
  nexts = set()
  with concurrent.futures.ProcessPoolExecutor(max_workers=8) as exe:
    for urls in exe.map(map1, arrs):
      for url in urls:
        nexts.add(url)
  #for arr in arrs:
  #  for url in map1(arr):
  #    nexts.add(url) 
  print(nexts)
  urls = nexts
