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
  index, names = arr
  _size = len(names)
  #print(index,names)
  for _index, name in enumerate(names):
    link_name = 'links/' + name.split('/').pop().replace('/', '_') 
    if os.path.exists(link_name) is True:
      continue

    print('now iter', _index, '/', _size, 'at', index)
    soup = bs4.BeautifulSoup( open(name).read() )
   
    f = open(link_name, 'w')
    for a in soup.find_all('a', href=True):
      url = a['href']
      try:
        if url[0] == '/':
          url = 'http://jin115.com' + url
      except Exception:
        continue
      
      if 'kakaku.com' not in url:
        continue

      f.write( url + '\n' ) 
import concurrent.futures
if '--map1' in sys.argv:
  arrs = {}
  for index, name in enumerate(files):
    key = index%32
    if arrs.get(key) is None:
      arrs[key] = []
    arrs[key].append( name )
  arrs = [ (index, names) for index,names in arrs.items() ]
  #_map(arrs[0])
  with concurrent.futures.ProcessPoolExecutor(max_workers=32) as exe:
    exe.map(_map, arrs)


if '--fold1' in sys.argv:
  urls = set()
  for index, name in enumerate(glob.glob('links/*')):
    print('now iter', index )
    [urls.add(url) for url in open(name).read().split('\n')]
  open('urls.pkl.gz', 'wb').write( gzip.compress(pickle.dumps(urls)) )

