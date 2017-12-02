import glob

import os

import bs4

from multiprocessing import Process

import sys

import pickle

import gzip
files = glob.glob('htmls/*')
size = len(files)

def _map(arr):
  index, name = arr
  link_name = 'links/' + name.split('/').pop().replace('/', '_') 
  if os.path.exists(link_name) is True:
    return

  print('now iter', index, '/', size)
  soup = bs4.BeautifulSoup( open(name).read() )
 
  f = open(link_name, 'w')
  for a in soup.find_all('a', href=True):
    url = a['href']
    try:
      if url[0] == '/':
        url = 'http://jin115.com' + url
    except Exception:
      continue
    
    if 'http://jin115.com' not in url:
      continue

    f.write( url + '\n' ) 

if '--map1' in sys.argv:
  for index, name in enumerate(files):
    p = Process(target=_map, args=((index, name), )) 
    p.start()

if '--fold1' in sys.argv:
  urls = set()
  for index, name in enumerate(glob.glob('links/*')):
    print('now iter', index )
    [urls.add(url) for url in open(name).read().split('\n')]
  open('urls.pkl.gz', 'wb').write( gzip.compress(pickle.dumps(urls)) )

