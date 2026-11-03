"""Import reviewed ordinary issues without replacing the curated catalogue.

Requires requests and Pillow. Run from the repository root.
The checked-in manifest is the reviewed input; downloads never infer issue dates.
Both images must decode before a record is added. Existing IDs are preserved.
"""
import concurrent.futures
import io
import json
import math
import zipfile
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from PIL import Image, ImageDraw, ImageFont


def build(row):
    note = dict(row)
    session = requests.Session()
    session.mount("http://", HTTPAdapter(max_retries=Retry(total=3, backoff_factor=1)))
    session.mount("https://", HTTPAdapter(max_retries=Retry(total=3, backoff_factor=1)))
    for side in ("front", "back"):
        url = note[side + "Original"]
        target = Path(f"public/notes/{note['id']}-{side}.jpg")
        if target.exists():
            with Image.open(target) as cached:
                cached.verify()
            note[side] = "./notes/" + target.name
            continue
        response = session.get(url, timeout=30)
        response.raise_for_status()
        data = response.content
        if note.get("imagePolicy") == "ecb-archive":
            data = zipfile.ZipFile(io.BytesIO(data)).read(note[side + "ArchiveMember"])
        image = Image.open(io.BytesIO(data)).convert("RGB")
        if min(image.size) < 80:
            raise ValueError(f"Undersized reference: {url}")
        if note.get("imagePolicy") == "snb-72dpi":
            width, height = [float(x.strip()) for x in note["dimensions"].split("×")]
            # SNB presents sixth-series portraits upright, rotated from landscape.
            if note["series"] == "Sixth series" and image.height > image.width:
                image = image.rotate(90, expand=True)
            image.thumbnail((math.floor(width / 25.4 * 72), math.floor(height / 25.4 * 72)))
            overlay = Image.new("RGBA", image.size)
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", max(14, min(image.size) // 5))
            draw = ImageDraw.Draw(overlay)
            draw.text((image.width / 2, image.height / 2), "SPECIMEN", font=font, anchor="mm", fill=(30, 30, 30, 230), stroke_width=1, stroke_fill=(255, 255, 255, 230))
            overlay = overlay.rotate(30)
            image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
        image.save(target, quality=92, dpi=(72, 72))
        note[side] = "./notes/" + target.name
    return note


if __name__ == "__main__":
    path = Path("src/notes.json")
    notes = json.loads(path.read_text())
    ids = {note["id"] for note in notes}
    rows = json.loads(Path("scripts/data/ordinary-series.json").read_text())
    pending = [row for row in rows if row["id"] not in ids]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        additions = list(pool.map(build, pending))
    notes.extend(additions)
    path.write_text(json.dumps(notes, ensure_ascii=False, indent=2) + "\n")
    print(f"Added {len(additions)} ordinary designs; {len(notes)} total")
