"""Build a static Pages artifact from explicitly referenced public assets only."""
from pathlib import Path
import re
import shutil

root = Path(__file__).resolve().parents[1]
output = root / '_site'
html = (root / 'index.html').read_text()
assets = set(re.findall(r'assets/[A-Za-z0-9_./-]+\.(?:png|jpg|jpeg|gif|webp|svg|mp4|webm)', html))
# Carousel posters use the video basename in JavaScript.
assets.update(str(Path(asset).with_suffix('.jpg')) for asset in list(assets) if asset.endswith('.mp4'))
if re.search(r'(?i)\.pdf\b', html):
    raise SystemExit('PDF reference found in HTML; publication stopped.')
for asset in assets:
    source = (root / asset).resolve()
    if not source.is_relative_to(root / 'assets') or not source.is_file():
        raise SystemExit(f'Invalid or missing public asset: {asset}')
if output.exists():
    shutil.rmtree(output)
output.mkdir()
shutil.copy2(root / 'index.html', output / 'index.html')
(output / '.nojekyll').touch()
for asset in sorted(assets):
    destination = output / asset
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / asset, destination)
files = [p for p in output.rglob('*') if p.is_file()]
assert not any(p.suffix.lower() == '.pdf' for p in files)
print(f'Prepared {len(files)} public files ({sum(p.stat().st_size for p in files) / 1024**2:.1f} MiB). No PDFs included.')
