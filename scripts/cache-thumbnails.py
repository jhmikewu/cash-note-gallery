"""Cache Wikimedia display-size images when original downloads are throttled."""
import concurrent.futures
import json
import subprocess
from pathlib import Path

catalog = Path('src/notes.json')
notes = json.loads(catalog.read_text())


def cache(task):
    note, side = task
    if note[side].startswith('./'):
        return None
    original = note[side]
    if 'upload.wikimedia.org/wikipedia/' not in original:
        return f'{note["id"]} {side}: unsupported source'
    prefix, relative = original.split('/wikipedia/', 1)
    collection, image_path = relative.split('/', 1)
    filename = image_path.rsplit('/', 1)[-1]
    extension = filename.rsplit('.', 1)[-1].lower()
    destination = Path(f'public/notes/{note["id"]}-{side}.{extension}')
    for width in (1280, 960, 640, 1920, 1024, 800, 1200, 500, 320):
        url = f'{prefix}/wikipedia/{collection}/thumb/{image_path}/{width}px-{filename}'
        result = subprocess.run(
            ['curl', '-fLs', '--max-time', '25', url], capture_output=True)
        if result.returncode or result.stdout[:3] not in (b'\xff\xd8\xff', b'\x89PN', b'RIF'):
            continue
        destination.write_bytes(result.stdout)
        note.setdefault(side + 'Original', original)
        note[side] = './notes/' + destination.name
        return None
    return f'{note["id"]} {side}'


with concurrent.futures.ThreadPoolExecutor(4) as pool:
    failures = [failure for failure in pool.map(
        cache, [(note, side) for note in notes for side in ('front', 'back')]) if failure]
catalog.write_text(json.dumps(notes, ensure_ascii=False, indent=2) + '\n')
print('Failures:', failures)
raise SystemExit(bool(failures))
