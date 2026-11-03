import subprocess, concurrent.futures
from bs4 import BeautifulSoup
urls=['https://www.bankofengland.co.uk/banknotes/polymer-5-pound-note','https://www.bankofengland.co.uk/banknotes/king-charles-banknotes','https://www.bankofcanada.ca/banknotes/','https://banknotes.rba.gov.au/banknote-features/banknotes-in-circulation/','https://www.bi.go.id/en/rupiah/gambar-uang/default.aspx','https://www.sama.gov.sa/en-US/Currency/Pages/SixthIssue.aspx','https://www.tcmb.gov.tr/wps/wcm/connect/en/tcmb+en/main+menu/banknotes/banknotes+in+circulation+and+their+security+features','https://www.pbc.gov.cn/en/3688229/3688335/3688341/index.html']
def run(url):
 s=BeautifulSoup(subprocess.run(['curl','-Ls','--max-time','30',url],capture_output=True).stdout,'html.parser')
 lines=[url]
 for im in s.select('img'):
  src=im.get('src','');alt=im.get('alt','')
  if not any(w in src.lower() for w in ['logo','icon','social','loading']):lines.append(src+' '+alt)
 return '\n'.join(lines)
print('\n\n'.join(concurrent.futures.ThreadPoolExecutor(8).map(run,urls)))
