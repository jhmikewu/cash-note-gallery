"""Optional maintenance fallback for Wikimedia throttling via a configured SSH host."""
import json,subprocess,concurrent.futures,sys,shlex
from pathlib import Path
notes=json.loads(Path('src/notes.json').read_text());host=sys.argv[1]
def run(t):
 n,side=t
 if n[side].startswith('./'):return
 url=n[side];ext=url.rsplit('.',1)[-1];dest=Path(f'public/notes/{n["id"]}-{side}.{ext}')
 r=subprocess.run(['ssh',host,'curl -fLs --compressed --max-time 30 '+shlex.quote(url)],capture_output=True)
 if r.returncode or r.stdout[:3] not in [b'\xff\xd8\xff',b'\x89PN',b'RIF']:return n['id']+' '+side
 dest.write_bytes(r.stdout);n[side]='./notes/'+dest.name
with concurrent.futures.ThreadPoolExecutor(3) as p: failures=[r for r in p.map(run,[(n,s) for n in notes for s in ['front','back']]) if r]
Path('src/notes.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2)+'\n');print('Failures',failures)
