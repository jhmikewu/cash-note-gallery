"""Cache reference images, preserving original URLs in the catalogue."""
import json,subprocess,concurrent.futures
from pathlib import Path
notes=json.loads(Path('src/notes.json').read_text())
sar={5:'SARW2020-005',10:'SAR0039',20:'SARW2020-020-comm',50:'SAR0040',100:'SAR0041',200:'SARW2021-200',500:'SAR0042'}
for n in notes:
 if n['currency']=='SAR':
  base='http://banknote.ws/COLLECTION/countries/ASI/SAR/'
  n['front']=base+sar[n['value']]+'os.jpg';n['back']=base+sar[n['value']]+'rs.jpg';n['imageSource']=base+'SAR.htm'
Path('public/notes').mkdir(parents=True,exist_ok=True)
def download(task):
 n,side=task;url=n.get(side+'Original') or n[side]
 if not url:return (n['id'],side,'missing')
 n[side+'Original']=url
 ext=url.split('?')[0].rsplit('.',1)[-1].lower();ext=ext if ext in ['png','jpg','jpeg','webp'] else 'jpg'
 target=Path(f'public/notes/{n["id"]}-{side}.{ext}')
 if not target.exists():
  fetchurl=url+('?cashnote=gallery' if 'wikimedia.org' in url and '?' not in url else '')
  r=subprocess.run(['curl','-fLs','--compressed','--max-time','15',fetchurl,'-o',str(target)],capture_output=True)
  if r.returncode:return(n['id'],side,'download failed')
 if target.read_bytes()[:3] not in [b'\xff\xd8\xff',b'\x89PN',b'RIF',b'GIF']:
  target.unlink();return(n['id'],side,'not an image')
 n[side]='./notes/'+target.name
 return None
results=list(concurrent.futures.ThreadPoolExecutor(4).map(download,[(n,s) for n in notes for s in ['front','back']]))
Path('src/notes.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2)+'\n')
print('Failures:',[r for r in results if r]);print('Cached',len(list(Path('public/notes').glob('*'))))
