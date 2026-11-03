"""Add reviewed PLN, TWD, ARS and ILS designs with attributed museum scans.

Issue dates/specifications: NBP circulating banknotes, CBC notes and coins,
BCRA billetes y monedas en vigencia, and Bank of Israel Series C.
Only adds missing records; existing curated records are preserved.
"""
import concurrent.futures
import json
import subprocess
from pathlib import Path

sources = {
    'PLN': 'https://nbp.pl/banknoty-i-monety/banknoty-obiegowe/',
    'TWD': 'https://www.cbc.gov.tw/public/data/issue/money/a1/t02.html',
    'ARS': 'https://www.bcra.gob.ar/billetes-y-monedas-en-vigencia/',
    'ILS': 'https://www.boi.org.il/en/economic-roles/banknotes-and-coins/third-series-of-the-new-shekel-2014/',
}
families = {
    'PLN': ('EUR/POL/', 'Polish rulers — modernised', 'Polish rulers and historic emblems. Earlier post-1995 designs also remain legal tender.'),
    'TWD': ('ASI/TWN/', 'Current New Taiwan dollar series', 'The current series celebrates history, education, sport, technology and Taiwan’s wildlife. Issue dates differ from the years printed on the notes.'),
    'ARS': ('AME/ARG/ARG-GENERAL/', 'Current peso designs', 'Argentina’s current peso notes include national figures and native wildlife. Earlier valid designs of these denominations circulate alongside them.'),
    'ILS': ('ASI/ISR/', 'Series C — Hebrew poets', 'Designed by Osnat Eshel. The series honours Hebrew poets and uses different lengths and tactile marks to distinguish denominations.'),
}
# Currency, value, introduction, portrait/theme, reverse, width, height, scan prefix.
rows = [
    ('PLN',10,2014,'Mieszko I','Silver denar',120,60,'POL0183'),
    ('PLN',20,2014,'Bolesław I the Brave','Medieval denar',126,63,'POL0184'),
    ('PLN',50,2014,'Casimir III the Great','Royal seal, orb and sceptre',132,66,'POL0185'),
    ('PLN',100,2014,'Władysław II Jagiełło','Eagle, swords and Malbork Castle',138,69,'POL0186'),
    ('PLN',200,2016,'Sigismund I the Old','Eagle and Wawel Castle courtyard',144,72,'POL0189'),
    ('PLN',500,2017,'John III Sobieski','Wilanów Palace',150,75,'POL0190'),
    ('TWD',100,2001,'Sun Yat-sen','Chung-Shan Building',145,70,'TWN1991'),
    ('TWD',200,2002,'Chiang Kai-shek','Presidential Office Building',150,70,'TWN1992'),
    ('TWD',500,2005,'Youth baseball team','Sika deer and Dabajian Mountain',155,70,'TWN1996'),
    ('TWD',1000,2005,'Schoolchildren','Mikado pheasants and Jade Mountain',160,70,'TWN1997'),
    ('TWD',2000,2002,'Satellite technology','Formosan salmon and Mount Nanhu',165,70,'TWN1995'),
    ('ARS',10,2016,'Manuel Belgrano','The first raising of the flag',155,65,'ARG0360'),
    ('ARS',20,2017,'Guanaco','Patagonian steppe',155,65,'ARG0361'),
    ('ARS',50,2018,'Andean condor','Aconcagua',155,65,'ARG0363'),
    ('ARS',100,2018,'Taruca deer','Famatina mountain range',155,65,'ARGW2018-0100'),
    ('ARS',200,2016,'Southern right whale','Valdés Peninsula',155,65,'ARG0364'),
    ('ARS',500,2016,'Jaguar','Yungas forest',155,65,'ARG0365'),
    ('ARS',1000,2023,'José de San Martín','Crossing of the Andes',155,65,'ARGW0367'),
    ('ARS',2000,2023,'Cecilia Grierson and Ramón Carrillo','Malbrán Institute',155,65,'ARGW0368'),
    ('ARS',10000,2024,'Manuel Belgrano and María Remedios del Valle','Oath to the flag',155,65,'ARGW0369'),
    ('ARS',20000,2024,'Juan Bautista Alberdi','Alberdi’s birthplace',155,65,'ARGW0370'),
    ('ILS',20,2017,'Rachel Bluwstein','Sea of Galilee',129,71,'ISR0065'),
    ('ILS',50,2014,'Shaul Tchernichovsky','Corinthian column',136,71,'ISR0066'),
    ('ILS',100,2017,'Leah Goldberg','Gazelles',143,71,'ISR0067'),
    ('ILS',200,2015,'Nathan Alterman','Moonlit flora',150,71,'ISR0068'),
]

def build(row):
    c,v,y,title,reverse,w,h,code = row
    directory,series,description = families[c]
    base = 'http://banknote.ws/COLLECTION/countries/' + directory
    note = dict(id=f'{c}-{v}', currency=c, value=v, year=y, title=title,
                reverseTitle=reverse, dimensions=f'{w} × {h}', material='Cotton paper',
                series=series, source=sources[c], imageSource=base+code+'.htm',
                status='Issued', orientation='Horizontal', description=description)
    prefix = code + ('-2013' if code=='ISR0066' else '')
    if c == 'ARS' and v in (20, 50, 100, 200, 500):
        note['orientation'] = 'Vertical'
        note['dimensions'] = '65 × 155'
    ext = 'JPG' if c=='TWD' and v!=2000 else 'jpg'
    for side,suffix in [('front','o'),('back','r')]:
        url = base+prefix+suffix+'.'+ext
        result = subprocess.run(['curl','-fLs','--retry','2','--max-time','30',url],capture_output=True,check=True)
        assert result.stdout[:3]==b'\xff\xd8\xff', url
        dest=Path(f'public/notes/{c}-{v}-{side}.jpg')
        dest.write_bytes(result.stdout)
        note[side]='./notes/'+dest.name
        note[side+'Original']=url
    return note

if __name__=='__main__':
    path=Path('src/notes.json')
    notes=json.loads(path.read_text())
    ids={n['id'] for n in notes}
    with concurrent.futures.ThreadPoolExecutor(4) as pool:
        notes.extend(pool.map(build,[r for r in rows if r[0] != 'TWD' and f'{r[0]}-{r[1]}' not in ids]))
    path.write_text(json.dumps(notes,ensure_ascii=False,indent=2)+'\n')
    print(f'{len(notes)} notes in catalogue')
