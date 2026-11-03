"""Curated China SAR and Swedish collections; preserve other records."""
import json, subprocess, concurrent.futures
from pathlib import Path

rows=[]
for v,y,w,t,b,code in [
 (20,2015,120,'Astrid Lindgren','Småland','SWE0069'),
 (50,2015,126,'Evert Taube','Bohuslän','SWE0070'),
 (100,2016,133,'Greta Garbo','Stockholm','SWE0071'),
 (200,2015,140,'Ingmar Bergman','Gotland','SWE0072'),
 (500,2016,147,'Birgit Nilsson','Skåne and Öresund Bridge','SWE0073'),
 (1000,2015,154,'Dag Hammarskjöld','Lappland','SWE0074')]:
 rows.append(('SEK',v,y,t,b,w,66,code))
rows.append(('HKD',10,2007,'Abstract design and bauhinia','Abstract design',138,69,'HKG0401'))
for v,y,b in [(20,2020,'Dim sum and tea culture'),(50,2020,'Butterflies'),(100,2019,'Cantonese opera'),(500,2019,'Hong Kong UNESCO Global Geopark'),(1000,2018,'International financial centre')]:
 i=[20,50,100,500,1000].index(v)
 rows.append(('HKD',v,y,'Bank of China Tower and bauhinia',b,143+5*i,71.5+2.5*i,f'HKGW2018-{v:04}-BOC'))
for i,(v,b) in enumerate([(10,'Macau Tower and skyline'),(20,'Macau Science Center'),(50,'Kiang Wu History Museum'),(100,'Tung Sin Tong Historical Archive'),(500,'A-Ma Temple'),(1000,'Traditional junk')]):
 rows.append(('MOP',v,2024+i//2,'Southern lion and Bank of China',b,138+5*i,69+2.5*i,f'MACW0{129+i}'))
sources={
 'SEK':'https://www.riksbank.se/en-gb/payments--cash/notes--coins/notes/valid-banknotes/',
 'HKD':'https://www.hkma.gov.hk/eng/key-functions/money/hong-kong-currency/notes/',
 'MOP':'https://www.amcm.gov.mo/en/currency/currency-in-circulation-in-macao/banknotes/new-series',
}
def build(row):
 c,v,y,t,b,w,h,code=row
 base='http://banknote.ws/COLLECTION/countries/'+{'SEK':'EUR/SWE/','HKD':'ASI/HKG/','MOP':'ASI/MAC/'}[c]
 prefix={'HKG0401':'HKG0401a','SWE0071':'SWE0071-1'}.get(code,code)
 n=dict(id=f'{c}-{v}',currency=c,value=v,year=y,title=t,reverseTitle=b,dimensions=f'{w} × {h}',material='Polymer' if c=='HKD' and v==10 else 'Cotton paper',series={'SEK':'2015–2016 series','HKD':'2018 series — Bank of China (Hong Kong)','MOP':'Southern Lion — Bank of China'}[c],status='Issued',orientation='Horizontal',source=sources[c],imageSource=base+code+'.htm',description={'SEK':'Swedish cultural figures and landscapes on cotton-paper notes.','HKD':'Hong Kong SAR, China, uses the Hong Kong dollar. This collection represents Bank of China (Hong Kong) issues; HSBC and Standard Chartered also issue legal-tender designs. The HK$10 is issued by the SAR Government.','MOP':'Macau SAR, China, uses the pataca. This collection represents Bank of China issues; Banco Nacional Ultramarino also issues legal-tender designs. The printed 2020 date precedes introduction in 2024–2026.'}[c])
 if c=='HKD' and v==10:n['series']='SAR Government polymer issue'
 if c=='HKD' and v!=10:n['backOrientation']='Vertical'
 for side,suffix in [('front','o'),('back','r')]:
  url=base+prefix+suffix+'.jpg';data=subprocess.check_output(['curl','-fLs','--retry','2','--max-time','30',url]);assert data[:3]==b'\xff\xd8\xff'
  path=Path(f'public/notes/{c}-{v}-{side}.jpg');path.write_bytes(data);n[side]='./notes/'+path.name;n[side+'Original']=url
 return n
if __name__=='__main__':
 path=Path('src/notes.json');notes=json.loads(path.read_text());notes=[n for n in notes if n['currency']!='TWD'];ids={n['id'] for n in notes}
 with concurrent.futures.ThreadPoolExecutor(4) as pool:notes.extend(pool.map(build,[r for r in rows if f'{r[0]}-{r[1]}' not in ids]))
 path.write_text(json.dumps(notes,ensure_ascii=False,indent=2)+'\n')
 for p in Path('public/notes').glob('TWD-*.jpg'):p.unlink()
 print(len(notes),'notes')
