"""Build the curated catalogue using reviewed source rows. Requires research.py output."""
import json,re,subprocess
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
research=json.loads(Path('/tmp/opencode/cash-research.json').read_text());notes=[]
def page(url):return BeautifulSoup(subprocess.run(['curl','-Ls','--compressed','--max-time','25',url],capture_output=True).stdout,'html.parser')
def original(u):
 u=u.split('?')[0]
 if u.startswith('//'):u='https:'+u
 if '/thumb/' in u:u=u.replace('thumb.wikimedia.org','upload.wikimedia.org').replace('/thumb/','/').rsplit('/',1)[0]
 return u
def add(c,v,y,title,back,dim,material='Cotton paper',series='Current series',row=None,front='',reverse='',source='',status='Issued',orientation='Horizontal',description=''):
 imageSource=source
 if row is not None:
  r=research[c]['rows'][row];ims=r['images'];front=original(ims[0]['url']);reverse=original(ims[1]['url']) if len(ims)>1 else ''
  imageSource=urljoin(research[c]['source'],ims[0]['file'] or '')
  source=source or research[c]['source']
 notes.append(dict(id=f'{c}-{v}',currency=c,value=v,year=y,title=title,reverseTitle=back,dimensions=dim,material=material,series=series,front=front,back=reverse,source=source,imageSource=imageSource,status=status,orientation=orientation,description=description))
us=page('https://www.uscurrency.gov/denominations')
for v,y,t,b in [(1,1963,'George Washington','The Great Seal'),(2,1976,'Thomas Jefferson','Declaration of Independence'),(5,2008,'Abraham Lincoln','Lincoln Memorial'),(10,2006,'Alexander Hamilton','US Treasury'),(20,2003,'Andrew Jackson','The White House'),(50,2004,'Ulysses S. Grant','US Capitol'),(100,2013,'Benjamin Franklin','Independence Hall')]:
 imgs=[urljoin('https://www.uscurrency.gov',i['src']) for i in us.select('img[src]') if f'/{v}_' in i['src'] or f'/{v}-' in i['src']]
 add('USD',v,y,t,b,'156 × 66','Cotton–linen','Federal Reserve notes',front=imgs[0],reverse=imgs[1],source=f'https://www.uscurrency.gov/denominations/{v}',description='US currency uses 75% cotton and 25% linen. All earlier US currency designs remain legal tender.')
for i,(v,y,t,w,h) in enumerate([(5,2013,'Classical architecture',120,62),(10,2014,'Romanesque architecture',127,67),(20,2015,'Gothic architecture',133,72),(50,2017,'Renaissance architecture',140,77),(100,2019,'Baroque and Rococo',147,77),(200,2019,'19th-century architecture',153,77),(500,2002,'Modern architecture',160,82)]):
 add('EUR',v,y,t,'European bridges',f'{w} × {h}',series='Europa' if v!=500 else 'First series',row=8+i if v!=500 else 7,source='https://www.ecb.europa.eu/euro/banknotes/current/html/index.en.html',status='Issued' if v!=500 else 'Not issued',description='The same euro banknotes circulate across the euro area. The €500 remains legal tender but has not been issued since 2019.' if v==500 else 'Windows and gateways represent openness; bridges on the reverse represent communication across Europe.')
for v,y,t,b,w,r in [(1000,2024,'Kitasato Shibasaburō','The Great Wave off Kanagawa',150,41),(2000,2000,'Shureimon gate','The Tale of Genji',154,37),(5000,2024,'Tsuda Umeko','Wisteria flowers',156,42),(10000,2024,'Shibusawa Eiichi','Tokyo Station',160,43)]:
 add('JPY',v,y,t,b,f'{w} × 76','Plant-fibre paper','Series F' if y==2024 else 'Series D',row=r,source='https://www.boj.or.jp/en/note_tfjgs/note/valid/issue.htm',status='Not issued' if v==2000 else 'Issued',description='The 2024 series uses three-dimensional holographic portraits. The ¥2,000 design remains valid and is uncommon outside Okinawa.')
for v,t,w,h in [(5,'Winston Churchill',125,65),(10,'Jane Austen',132,69),(20,'J. M. W. Turner',139,73),(50,'Alan Turing',146,77)]:
 base='https://www.bankofengland.co.uk/-/media/boe/images/banknotes/king-charles/'
 add('GBP',v,2024,'King Charles III',t,f'{w} × {h}','Polymer','King Charles III',front=base+f'kc-{v}-pound.jpg',reverse=base+f'{v}back.jpg',source='https://www.bankofengland.co.uk/banknotes/king-charles-banknotes',description='First issued on 5 June 2024. Queen Elizabeth II polymer notes also remain legal tender. This collection covers Bank of England issues.')
for i,(v,y,b,w,h) in enumerate([(10,2018,'Konark Sun Temple',123,63),(20,2019,'Ellora Caves',129,63),(50,2017,'Hampi stone chariot',135,66),(100,2018,'Rani ki Vav',142,66),(200,2017,'Sanchi Stupa',146,66),(500,2016,'Red Fort',150,66),(2000,2016,'Mangalyaan',166,66)]):
 add('INR',v,y,'Mahatma Gandhi',b,f'{w} × {h}',series='Mahatma Gandhi New Series',row=i,source='https://www.rbi.org.in/CommonPerson/english/currency/scripts/banknotes.aspx',status='Withdrawing' if v==2000 else 'Issued',description='The ₹2,000 note was withdrawn from circulation in 2023 but continues to be legal tender; return and exchange arrangements apply.' if v==2000 else 'The reverse celebrates India’s cultural and scientific heritage. The design incorporates a portrait watermark and security thread.')
for i,(v,y,b,w,h) in enumerate([(2,2013,'Hawksbill turtle',121,65),(5,2013,'Great egret',128,65),(10,2012,'Green-winged macaw',135,65),(20,2012,'Golden lion tamarin',142,65),(50,2010,'Jaguar',149,70),(100,2010,'Dusky grouper',156,70),(200,2020,'Maned wolf',142,65)]):
 add('BRL',v,y,'Effigy of the Republic',b,f'{w} × {h}',series='Second family',row=35+i,source='https://www.bcb.gov.br/en/banknotesandcoins/secondseriesbanknotes',description='Brazil’s second family pairs the symbolic Republic with native wildlife. Denominations use different sizes to aid identification.')
for i,(v,y,t,b,w) in enumerate([(1000,2007,'Yi Hwang','Gyesangjeonggeodo',136),(5000,2006,'Yi I','Insects and Plants',142),(10000,2007,'Sejong the Great','Astronomy and celestial globe',148),(50000,2009,'Shin Saimdang','Bamboo and plum tree',154)]):
 add('KRW',v,y,t,b,f'{w} × 68',row=42+i,source='https://www.bok.or.kr/eng/main/contents.do?menuNo=400110',description='Korea’s notes celebrate scholars, artists, and scientific achievement. Their different lengths help distinguish the denominations.')
for i,(v,y,t,b,w) in enumerate([(20,2021,'Mexican independence','Sian Ka’an mangroves',120),(50,2021,'Foundation of Tenochtitlan','Axolotl and Xochimilco',125),(100,2020,'Sor Juana Inés de la Cruz','Monarch butterflies',132),(200,2019,'Hidalgo and Morelos','Golden eagle',139),(500,2018,'Benito Juárez','Gray whale',146),(1000,2020,'Madero, Galindo and Serdán','Jaguar and Calakmul',153)]):
 add('MXN',v,y,t,b,f'{w} × 65','Polymer' if v<=100 else 'Cotton paper','Family G',row=71+i,orientation='Vertical' if v in [50,100] else 'Horizontal',source='https://www.banxico.org.mx/banknotes-and-coins/banknotes-in-circulation.html',description='The front traces Mexican history; the reverse celebrates Mexico’s ecosystems and natural heritage.')
for i,(v,y,t) in enumerate([(10,2017,'Time'),(20,2017,'Light'),(50,2016,'Wind'),(100,2019,'Water'),(200,2018,'Matter'),(1000,2019,'Language')]):
 add('CHF',v,y,t,'Switzerland’s many facets',f'70 × {123+i*7}','Hybrid','Ninth series',row=39+i,orientation='Vertical',source='https://www.snb.ch/en/the-snb/mandates-goals/cash/banknotes/9-series',description='Designed by Manuela Pfrunder, the ninth series explores facets of Switzerland through hands, globes, and landscapes. Durasafe combines cotton paper with a polymer core.')
for v,y,t,b,w,word in [(5,2016,'Queen Elizabeth II','Parliament House',130,'five'),(10,2017,'Banjo Paterson','Dame Mary Gilmore',137,'ten'),(20,2019,'Mary Reibey','John Flynn',144,'twenty'),(50,2018,'David Unaipon','Edith Cowan',151,'fifty'),(100,2020,'Dame Nellie Melba','Sir John Monash',158,'hundred')]:
 base=f'https://banknotes.rba.gov.au/banknote-features/images/new-{word}/new-{word}-banknote'
 add('AUD',v,y,t,b,f'{w} × 65','Polymer','Next Generation',front=base+'.jpg',reverse=base+'-flipped.jpg',source='https://banknotes.rba.gov.au/banknote-features/explore/',description='A top-to-bottom clear window contains dynamic security features. Raised tactile bumps help people with vision impairment identify the value.')
cn=page('https://zh.wikipedia.org/wiki/第五套人民币')
for v,y,b,w,h in [(1,2019,'West Lake',130,63),(5,2020,'Mount Tai',135,63),(10,2019,'Three Gorges',140,70),(20,2019,'Li River, Guilin',145,70),(50,2019,'Potala Palace',150,70),(100,2015,'Great Hall of the People',155,77)]:
 ims=[original(im['src']) for im in cn.select('img[src]') if f'/{v}-{y}' in im['src']]
 if v==100:ims=[original(im['src']) for im in cn.select('img[src]') if '100' in im['src'] and ('2015' in im['src'])]
 add('CNY',v,y,'Mao Zedong',b,f'{w} × {h}',series='Fifth series',front=ims[0] if ims else '',reverse=ims[1] if len(ims)>1 else '',source='https://en.wikipedia.org/wiki/Fifth_series_of_the_renminbi',description='The fifth series pairs a portrait of Mao Zedong with landscapes and landmarks across China.')
tr=page('https://en.wikipedia.org/wiki/Turkish_lira')
for v,t,w,h in [(5,'Aydın Sayılı',130,64),(10,'Cahit Arf',136,64),(20,'Mimar Kemaleddin',142,68),(50,'Fatma Aliye',148,68),(100,'Buhurizade Mustafa Itri',154,72),(200,'Yunus Emre',160,72)]:
 ims=[original(im['src']) for im in tr.select('img[src]') if (f'/{v}_T%C3%BCrk' in im['src'] if v!=5 else '/5-II_T%C3%BCrk' in im['src'])]
 add('TRY',v,2013 if v==5 else 2009,'Mustafa Kemal Atatürk',t,f'{w} × {h}',series='E9',front=ims[0],reverse=ims[1],source='https://en.wikipedia.org/wiki/Turkish_lira',description='The E9 series celebrates Turkish contributors to science, architecture, literature and music. The purple 5-lira design was introduced in 2013.')
for v,y,t,b in [(5,2013,'Wilfrid Laurier','Canadarm2 and Dextre'),(10,2018,'Viola Desmond','Canadian Museum for Human Rights'),(20,2012,'Queen Elizabeth II','Canadian National Vimy Memorial'),(50,2012,'William Lyon Mackenzie King','CCGS Amundsen'),(100,2011,'Robert Borden','Medical research')]:
 url=f'https://www.bankofcanada.ca/banknotes/bank-note-series/frontiers/{v}-polymer-note/'
 s=page(url) if v!=10 else page('https://www.bankofcanada.ca/banknotes/vertical10/')
 ims=[im['src'] for im in s.select('img[src]') if re.search(fr'/{v}_(front|back)\.',im['src'])]
 if v==10:ims=[im['src'] for im in s.select('img[src]') if any(x in im['src'].lower() for x in ['10_front','10_back','10-front','10-back'])]
 add('CAD',v,y,t,b,'70 × 152' if v==10 else '152 × 70','Polymer','Vertical series' if v==10 else 'Frontiers',front=ims[0] if ims else '',reverse=ims[1] if len(ims)>1 else '',orientation='Vertical' if v==10 else 'Horizontal',source=url if v!=10 else 'https://www.bankofcanada.ca/banknotes/vertical10/',description='Canadian polymer notes include a transparent window with metallic imagery. The vertical $10 honours civil-rights pioneer Viola Desmond.')
for i,(v,t,b) in enumerate([(1000,'Tjut Meutia','Tifa dance and Banda Neira'),(2000,'Mohammad Husni Thamrin','Piring dance and Sianok Canyon'),(5000,'Idham Chalid','Gambyong dance and Mount Bromo'),(10000,'Frans Kaisiepo','Pakarena dance and Wakatobi'),(20000,'Sam Ratulangi','Gong dance and Derawan Islands'),(50000,'Djuanda Kartawidjaja','Legong dance and Komodo'),(100000,'Sukarno and Mohammad Hatta','Topeng Betawi and Raja Ampat')]):
 base=f'https://www.bi.go.id/Gambar%20Uang/TE2022/TE-2022-{v}-'
 add('IDR',v,2022,t,b,f'{121+5*i} × 65',series='2022 emission',front=base+'depan.JPG',reverse=base+'belakang.JPG',source='https://www.bi.go.id/en/rupiah/gambar-uang/default.aspx',description='The 2022 series celebrates national heroes, traditional dances and Indonesian landscapes, with stronger colour contrast and improved security.')
for v,y,t,b,w,h,r in [(5,1998,'Veliky Novgorod','Novgorod Kremlin',137,61,20),(10,1998,'Krasnoyarsk','Krasnoyarsk hydroelectric station',150,65,21),(50,1998,'Saint Petersburg','Old Stock Exchange',150,65,25),(100,2022,'Moscow','Rzhev memorial',150,65,39),(200,2017,'Monument to the Sunken Ships','Chersonesus',150,65,41),(500,1998,'Arkhangelsk','Solovetsky Monastery',150,65,31),(1000,2025,'Nizhny Novgorod','Volga region',157,69,42),(2000,2017,'Russky Bridge','Vostochny Cosmodrome',157,69,43),(5000,2023,'Yekaterinburg','Ural region',157,69,44)]:
 add('RUB',v,y,t,b,f'{w} × {h}',series='Bank of Russia',row=r,source='https://www.cbr.ru/eng/cash_circulation/banknotes/',description='Bank of Russia notes depict cities and regions. The 200-ruble imagery depicts locations in Crimea, internationally recognised as part of Ukraine.' if v==200 else 'Bank of Russia notes celebrate the architecture, monuments and landscapes of cities and regions.')
for v,y,t,b,w,h in [(5,2020,'King Salman','Flowers',145,66),(10,2016,'King Salman','King Abdullah Financial District',150,68),(20,2020,'King Salman','G20 world map',152,69),(50,2016,'King Salman','Al-Aqsa Mosque',155,70),(100,2016,'King Salman','Prophet’s Mosque',160,72),(200,2021,'King Abdulaziz','Al-Hukm Palace',163,73),(500,2016,'King Abdulaziz','Masjid al-Haram',166,74)]:
 add('SAR',v,y,t,b,f'{w} × {h}','Polymer' if v==5 else 'Cotton paper','Sixth series / commemorative' if v in [20,200] else 'Sixth series',source='https://en.wikipedia.org/wiki/Saudi_riyal',description='The sixth series depicts Saudi kings and significant landmarks. The 20- and 200-riyal notes are commemorative issues.')
Path('src/notes.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2)+'\n')
print(len(notes),'notes built. Missing images:',[(n['id'],s) for n in notes for s in ['front','back'] if not n[s]])
