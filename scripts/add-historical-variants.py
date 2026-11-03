"""Add reviewed Bank of England design variants without overwriting existing records.

Requires Pillow. Issuer images retain their supplied SPECIMEN markings.
Withdrawal dates: https://www.bankofengland.co.uk/banknotes/withdrawn-banknotes
"""
import copy
import io
import json
import subprocess
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://www.bankofengland.co.uk'
notes = json.loads((ROOT / 'src/notes.json').read_text())
existing = {n['id'] for n in notes}

def image(url, ident, side, half=None):
    data = subprocess.check_output(['curl', '-fLs', '--retry', '2', '--max-time', '40', url])
    im = Image.open(io.BytesIO(data)).convert('RGB')
    if half is not None:
        # Issuer archive plates contain front above reverse; preserve both markings.
        w, h = im.size
        im = im.crop((0, 0 if half == 0 else h//2, w, h//2 if half == 0 else h))
    dest = ROOT / f'public/notes/{ident}-{side}.jpg'
    im.save(dest, quality=93)
    return './notes/' + dest.name

def add(value, start, end, series, reverse, dimensions, paths, combined=False):
    ident = f'GBP-{value}-{start[:4]}'
    if ident in existing:
        return
    note = copy.deepcopy(next(n for n in notes if n['id'] == f'GBP-{value}'))
    note.update(id=ident, year=int(start[:4]), circulationStart=start,
                circulationEnd=end, title='Queen Elizabeth II', reverseTitle=reverse,
                series=series, dimensions=dimensions,
                material='Cotton paper' if end else 'Polymer',
                status='Withdrawn' if end else 'Issued',
                source=BASE+'/banknotes/'+('withdrawn-banknotes' if end else 'current-banknotes'),
                description=('Withdrawn from circulation; the Bank of England still exchanges this note.' if end else
                             'Queen Elizabeth II polymer notes remain legal tender alongside King Charles III notes.'),
                reproductionSource=BASE+'/banknotes/using-images-of-banknotes',
                imageTreatment='Issuer-supplied SPECIMEN marking retained')
    for index, side in enumerate(['front', 'back']):
        url = BASE+'/-/media/boe/images/banknotes/'+paths[index]
        note[side] = image(url, ident, side, index if combined else None)
        note[side+'Original'] = url
    note['imageSource'] = note['frontOriginal']
    notes.append(note)
    print(ident, flush=True)

for v,start,back,dim,paths in [
    (5,'2016-09-13','Winston Churchill','125 × 65',['5/5-front-specimen.jpeg','5/5-back-specimen.jpeg']),
    (10,'2017-09-14','Jane Austen','132 × 69',['10/10-front.jpg','10/polymer-10-back-specimen.jpg']),
    (20,'2020-02-20','J. M. W. Turner','139 × 73',['20/polymer/polymer-20-specimen-front-(1).jpg','20/polymer/polymer-20-specimen-back.jpg']),
    (50,'2021-06-23','Alan Turing','146 × 77',['50/polymer/polymer-50-specimen-front.jpg','50/polymer/polymer-50-specimen-back.jpg']),
]:
    add(v,start,None,'Queen Elizabeth II — polymer',back,dim,paths)

for v,start,end,series,back,dim,file in [
    (5,'1990-06-07','2003-11-21','Series E','George Stephenson','135 × 70','5e-1990-1990041.jpg'),
    (5,'1993-03-01','2003-11-21','Series E — revised','George Stephenson','135 × 70','5e-revised-1999006.jpg'),
    (10,'1992-04-29','2003-07-31','Series E','Charles Dickens','142 × 75','10e-1992123.jpg'),
    (10,'1993-11-22','2003-07-31','Series E — revised','Charles Dickens','142 × 75','10e-revised-1999003.jpg'),
    (20,'1991-06-05','2001-02-28','Series E','Michael Faraday','149 × 80','20e-1991-1991108.jpg'),
    (20,'1993-09-27','2001-02-28','Series E — revised','Michael Faraday','149 × 80','20e-revised-1999008.jpg'),
    (50,'1994-04-20','2014-04-30','Series E','Sir John Houblon','156 × 85','50e-1994-1994086.jpg'),
    (20,'1999-06-22','2010-06-30','Series E — variant','Edward Elgar','149 × 80','20e-var-1999-1999085.jpg'),
    (10,'2000-11-07','2018-03-01','Series E — variant','Charles Darwin','142 × 75','10seriesv.jpg'),
    (5,'2002-05-21','2017-05-05','Series E — variant','Elizabeth Fry','135 × 70','5e-var-2002-2002022.jpg'),
    (20,'2007-03-13','2022-09-30','Series F','Adam Smith','149 × 80','20-series-f.jpg'),
    (50,'2011-11-02','2022-09-30','Series F','Matthew Boulton and James Watt','156 × 85','50-series-f.png'),
]:
    add(v,start,end,series,back,dim,['withdrawn/'+file]*2,True)

for note in notes:
    note.setdefault('circulationStart', str(note['year']))
    note.setdefault('circulationEnd', None)
(ROOT/'src/notes.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2)+'\n')
print(len(notes), 'notes')
