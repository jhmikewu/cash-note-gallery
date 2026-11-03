"""Use attributed full-size museum scans where issuer downloads are unavailable."""
import json,subprocess,concurrent.futures
from pathlib import Path
notes=json.loads(Path('src/notes.json').read_text())
sar={5:'SARW2020-005',10:'SAR0039',20:'SARW2020-020-comm',50:'SAR0040',100:'SAR0041',200:'SARW2021-200',500:'SAR0042'}
tasks=[]
for n in notes:
 if n['currency'] not in ['SAR','IDR']:continue
 code=sar[n['value']] if n['currency']=='SAR' else 'INOW0'+str(162+[1000,2000,5000,10000,20000,50000,100000].index(n['value']))
 base='http://banknote.ws/COLLECTION/countries/ASI/'+('SAR' if n['currency']=='SAR' else 'INO')+'/'
 n['imageSource']=base+code+'.htm'
 for side,suffix in [('front','o'),('back','r')]:tasks.append((n,side,base+code+suffix+'.jpg'))
def run(t):
 n,side,url=t;dest=f'public/notes/{n["id"]}-{side}.jpg'
 subprocess.run(['curl','-fLs','--compressed','--max-time','20',url,'-o',dest],check=True)
 assert Path(dest).read_bytes()[:3]==b'\xff\xd8\xff'
 n[side]='./notes/'+Path(dest).name;n[side+'Original']=url
with concurrent.futures.ThreadPoolExecutor(4) as pool:list(pool.map(run,tasks))
Path('src/notes.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2)+'\n')
