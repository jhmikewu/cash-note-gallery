"""Reviewed corrections after comparing source images to metadata."""
import json,shutil
from pathlib import Path
data=json.loads(Path('src/notes.json').read_text())
for n in data:
 if n['id']=='CAD-10':
  for side,num in [('front',196440),('back',196441)]:
   n[side+'Original']=f'https://www.bankofcanada.ca/wp-content/uploads/2018/01/{num}.png'
   n[side]=n[side+'Original']
   Path(f'public/notes/CAD-10-{side}.png').unlink(missing_ok=True)
 if n['id']=='CNY-100':
  n['frontOriginal']='https://upload.wikimedia.org/wikipedia/zh/5/51/100-2015-b.jpg'
  n['backOriginal']='https://upload.wikimedia.org/wikipedia/zh/c/cc/100-2015-a.jpg'
  for side in ['front','back']:
   n[side]=n[side+'Original'];Path(f'public/notes/CNY-100-{side}.jpg').unlink(missing_ok=True)
 if n['id']=='RUB-50':n['year']=2001
 if n['id']=='RUB-500':n['year']=2001
Path('src/notes.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
