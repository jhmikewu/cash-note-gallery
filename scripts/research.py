"""Collect reference tables and image URLs for manual catalogue curation."""
import requests, concurrent.futures, json, subprocess
from bs4 import BeautifulSoup
from pathlib import Path
PAGES={'CNY':'Fifth_series_of_the_renminbi','EUR':'Euro_banknotes','JPY':'Banknotes_of_the_Japanese_yen','GBP':'Banknotes_of_the_pound_sterling','INR':'Mahatma_Gandhi_New_Series','RUB':'Russian_ruble','BRL':'Brazilian_real','CAD':'Banknotes_of_the_Canadian_dollar','KRW':'South_Korean_won','MXN':'Mexican_peso','AUD':'Banknotes_of_the_Australian_dollar','TRY':'Banknotes_of_the_Republic_of_Turkey','IDR':'Indonesian_rupiah','SAR':'Saudi_riyal','CHF':'Banknotes_of_the_Swiss_franc'}
def fetch(item):
 code,page=item
 url='https://en.wikipedia.org/wiki/'+page
 html=subprocess.check_output(['curl','-Ls','--max-time','40',url]).decode()
 s=BeautifulSoup(html,'html.parser')
 tables=[]
 for t in s.select('table'):
  if not t.select('img'): continue
  rows=[]
  for row in t.select('tr'):
   imgs=[{'url':i.get('src'),'alt':i.get('alt'),'file':i.parent.get('href')} for i in row.select('img')]
   if imgs: rows.append({'text':row.get_text(' ',strip=True),'images':imgs})
  tables.extend(rows)
 return code,{'source':url,'rows':tables}
if __name__=='__main__':
 results=dict(concurrent.futures.ThreadPoolExecutor(8).map(fetch,PAGES.items()))
 Path('/tmp/opencode/cash-research.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
 for code,data in results.items():
  print('\n'+code)
  for i,r in enumerate(data['rows']):
   if len(r['text'])<1600: print(i,r['text'][:380], [im['url'].split('/')[-1][:80] for im in r['images']][:2])
