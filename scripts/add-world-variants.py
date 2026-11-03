"""Reviewed major historical designs; requires saved research rows and Pillow.

Run from project root. Does not rerun the destructive original catalogue builder.
"""
import copy, io, json, re, subprocess
from pathlib import Path
from PIL import Image

notes=json.loads(Path('src/notes.json').read_text())
research=json.loads(Path('/tmp/opencode/cash-research.json').read_text())

def cache(url, ident, side):
    url='https:'+url if url.startswith('//') else url
    url=url.split('?')[0]
    candidates=[url]
    if '/thumb/' in url:
        candidates=[re.sub(r'/\d+px-',f'/{w}px-',url) for w in [960,640,320,120]]
    for u in candidates:
        r=subprocess.run(['curl','-fLs','--max-time','20',u],capture_output=True)
        try: im=Image.open(io.BytesIO(r.stdout)).convert('RGB')
        except Exception: continue
        dest=Path(f'public/notes/{ident}-{side}.jpg');im.save(dest,quality=92)
        return './notes/'+dest.name,url
    raise RuntimeError('Image unavailable: '+url)

def add(c,v,start,series,title,back,dim,row,end=None,material='Cotton paper',orientation='Horizontal',source=None):
    ident=f'{c}-{v}-{start[:4]}'
    if any(n['id']==ident for n in notes):return
    n=copy.deepcopy(next(n for n in notes if n['currency']==c))
    n.update(id=ident,value=v,year=int(start[:4]),circulationStart=start,circulationEnd=end,
             series=series,title=title,reverseTitle=back,dimensions=dim,material=material,
             orientation=orientation,status='Withdrawn' if end else 'Not issued',
             source=source or research[c]['source'],description=f'{series}. '+('Withdrawn from circulation; exchange arrangements are separate.' if end else 'Earlier design; stopping issuance does not remove legal-tender status.'))
    n.pop('backOrientation',None)
    if c == 'BRL':
        n.update(status='Withdrawing',source='https://www.bcb.gov.br/cedulasemoedas/cedulas',
                 description='Earlier real design. Banks are collecting these notes, but they remain valid for payment; no final withdrawal date is established.')
    for i,side in enumerate(['front','back']):
        im=research[c]['rows'][row]['images'][i]
        n[side],n[side+'Original']=cache(im['url'],ident,side)
    n['imageSource']=research[c]['rows'][row]['images'][0]['file']
    notes.append(n)
    Path('src/notes.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2)+'\n')
    print(ident,flush=True)

for row,v,start,t,b,w,series in [
    (34,1000,'1984-11-01','Natsume Sōseki','Pair of cranes',150,'Series D'),
    (35,5000,'1984-11-01','Nitobe Inazō','Mount Fuji and Lake Motosu',155,'Series D'),
    (36,10000,'1984-11-01','Fukuzawa Yukichi','Pair of pheasants',160,'Series D'),
    (38,1000,'2004-11-01','Noguchi Hideyo','Mount Fuji and cherry blossoms',150,'Series E'),
    (39,5000,'2004-11-01','Higuchi Ichiyō','Irises by Ogata Kōrin',156,'Series E'),
    (40,10000,'2004-11-01','Fukuzawa Yukichi','Phoenix at Byōdō-in',160,'Series E'),
]:
    add('JPY',v,start,series,t,b,f'{w} × 76',row,material='Plant-fibre paper',source='https://www.boj.or.jp/en/note_tfjgs/note/valid/issue.htm')

for row,v,y,b in [(27,1,1994,'Hummingbird'),(28,2,2001,'Hawksbill turtle'),(29,5,1994,'Great egret'),(30,10,1994,'Green-winged macaw'),(31,20,2002,'Golden lion tamarin'),(32,50,1994,'Jaguar'),(33,100,1994,'Dusky grouper')]:
    add('BRL',v,str(y),'First family','Effigy of the Republic',b,'140 × 65',row,source='https://www.bcb.gov.br/cedulasemoedas/cedulasprimeirafamilia')
add('BRL',10,'2000','500 years commemorative','Pedro Álvares Cabral','Map and people of Brazil','140 × 65',34,material='Polymer')
