"""Add Canadian Journey/Birds and Australian first-polymer designs.

Requires requests, BeautifulSoup and Pillow. Canadian reference copies carry a
SPECIMEN overlay as required for flat digital reproductions. Australian copies
are limited to 72 dpi at 74% of original dimensions.
"""
import copy, io, json, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup

def get(url):
    return subprocess.check_output(['curl','-fLs','--retry','2','--max-time','30',url])

def save(note,side,url,mark=False):
    im=Image.open(io.BytesIO(get(url))).convert('RGB')
    if mark:
        layer=Image.new('RGBA',im.size)
        font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',max(20,im.width//10))
        draw=ImageDraw.Draw(layer)
        draw.text((im.width/2,im.height/2),'SPECIMEN',font=font,fill=(35,35,35,255),stroke_width=1,stroke_fill='white',anchor='mm')
        layer=layer.rotate(25)
        im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
    else:
        w,h=map(float,note['dimensions'].split(' × '))
        im.thumbnail((int(w/25.4*72*.74),int(h/25.4*72*.74)))
    p=Path(f"public/notes/{note['id']}-{side}.jpg");im.save(p,quality=93,dpi=(72,72))
    note[side]='./notes/'+p.name;note[side+'Original']=url

def main():
    notes=json.loads(Path('src/notes.json').read_text())
    for v,y,word in [(5,1995,'five'),(10,1993,'ten'),(20,1994,'twenty'),(50,1995,'fifty'),(100,1996,'hundred')]:
        ident=f'AUD-{v}-{y}'
        if any(n['id']==ident for n in notes):continue
        n=copy.deepcopy(next(n for n in notes if n['id']==f'AUD-{v}'))
        n.update(id=ident,year=y,circulationStart=str(y),circulationEnd=None,status='Not issued',series='First polymer series'+(' — brighter colours' if v==5 else ''),
                 source='https://banknotes.rba.gov.au/australias-banknotes/history/',
                 description='Earlier polymer design. Australian banknotes from this series remain legal tender.',
                 reproductionSource='https://banknotes.rba.gov.au/legal/reproducing-banknotes/',
                 imageTreatment='Reference image limited to 72 dpi at 74% genuine dimensions')
        for side,suffix in [('front',''),('back','-flipped')]:
            save(n,side,f'https://banknotes.rba.gov.au/banknote-features/images/{word}/{word}-banknote{suffix}.jpg')
        n['imageSource']=n['frontOriginal'];notes.append(n);print(ident,flush=True)
    for slug,series,rows in [
        ('1986-the-birds-of-canada-series','Birds of Canada',[(2,1986,'Queen Elizabeth II','American robins'),(5,1986,'Wilfrid Laurier','Belted kingfisher'),(10,1989,'John A. Macdonald','Osprey'),(20,1991,'Queen Elizabeth II','Common loon'),(50,1989,'William Lyon Mackenzie King','Snowy owl'),(100,1990,'Robert Borden','Canada geese'),(1000,1992,'Queen Elizabeth II','Pine grosbeaks')]),
        ('2001-2006-canadian-journey-series','Canadian Journey',[(5,2002,'Wilfrid Laurier','Children at play'),(10,2001,'John A. Macdonald','Remembrance and peacekeeping'),(20,2004,'Queen Elizabeth II','Art by Bill Reid'),(50,2004,'William Lyon Mackenzie King','Nation building and women’s rights'),(100,2004,'Robert Borden','Exploration and innovation')]),
    ]:
        base='https://www.bankofcanadamuseum.ca/complete-bank-note-series/'+slug+'/'
        page=BeautifulSoup(get(base),'html.parser')
        for v,y,t,b in rows:
            ident=f'CAD-{v}-{y}'
            if any(n['id']==ident for n in notes):continue
            link=next(a['href'] for a in page.select('a[href]') if a.text.strip().endswith(f'${v:,} Note'))
            detail=BeautifulSoup(get(link),'html.parser')
            images=[i['src'] for i in detail.select('img[src]') if any(x in i['src'] for x in ['recto','verso']) and '500x250' not in i['src']]
            if len(images)!=2:raise RuntimeError(f'{ident}: review image selection {images}')
            n=copy.deepcopy(next(n for n in notes if n['id']=='CAD-20'))
            n.update(id=ident,value=v,year=y,circulationStart=str(y),circulationEnd='2020-12-31' if v in [2,1000] else None,
                     title=t,reverseTitle=b,series=series,material='Cotton paper',dimensions='152 × 70',
                     status='Withdrawn' if v in [2,1000] else 'Not issued',source=link,imageSource=link,
                     description='Earlier Canadian paper design. '+('Legal tender status removed on 1 January 2021; redemption remains available.' if v in [2,1000] else 'This denomination remains legal tender; paper designs are no longer issued.'),
                     reproductionSource='https://www.bankofcanada.ca/banknotes/using-bank-note-images/',imageTreatment='SPECIMEN added to reference reproduction')
            for side,u in zip(['front','back'],images):save(n,side,u,True)
            if n['circulationEnd']:
                n['circulationSource']='https://www.bankofcanada.ca/2021/01/about-legal-tender/'
            notes.append(n);print(ident,flush=True)
    Path('src/notes.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
