"""Clone the pinned public ledger and restore this project's offline source snapshot."""
import argparse
import csv
import hashlib
import io
from pathlib import Path
import subprocess
import sys
import zipfile

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
from ask_filings.dependency import LOCK, default_ledger


def restore(root):
    archive = PROJECT / 'fixtures/frozen-ledger.zip'
    if hashlib.sha256(archive.read_bytes()).hexdigest() != LOCK['archive_sha256']:
        raise ValueError('frozen archive hash mismatch')
    with zipfile.ZipFile(archive) as z:
        # Validate the complete bundle before any writes. No links or executable source.
        for name in z.namelist():
            path = Path(name)
            if path.is_absolute() or '..' in path.parts or path.parts[0] != 'data':
                raise ValueError('unsafe archive path')
        for name, expected in LOCK['tables'].items():
            if hashlib.sha256(z.read('data/' + name)).hexdigest() != expected:
                raise ValueError('table hash mismatch')
        manifest = z.read('data/raw/manifest.csv')
        if hashlib.sha256(manifest).hexdigest() != LOCK['source_manifest_sha256']:
            raise ValueError('source manifest hash mismatch')
        rows = list(csv.DictReader(io.StringIO(manifest.decode())))
        if len(rows) != LOCK['source_documents']:
            raise ValueError('source document count mismatch')
        for row in rows:
            body = z.read('data/raw/' + row['path'])
            if hashlib.sha256(body).hexdigest() != row['sha256'] or len(body) != int(row['bytes']):
                raise ValueError('source hash mismatch')
        for name in z.namelist():
            target = root / name
            # Refuse pre-existing symlink paths instead of following them outside the checkout.
            if any(p.is_symlink() for p in (target, *target.parents)):
                raise ValueError('refusing symlink in restore path')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(z.read(name))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ledger', type=Path, default=default_ledger())
    p.add_argument('--offline', action='store_true', help='require the pinned checkout already present')
    a = p.parse_args()
    root = a.ledger.absolute()
    if not root.exists():
        if a.offline:
            p.error('pinned checkout missing; run setup once with GitHub access')
        root.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['git', 'clone', '--no-checkout', LOCK['repository'], str(root)], check=True)
        subprocess.run(['git', '-C', str(root), 'checkout', '--detach', LOCK['commit']], check=True)
    actual = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    if actual != LOCK['commit']:
        p.error('checkout differs from pin; use a new empty directory')
    restore(root)
    print(f'Restored {LOCK["source_documents"]} verified source documents to {root}')
    print('Answers and tests now run offline. Use --ledger or ASK_FILINGS_LEDGER for custom locations.')


if __name__ == '__main__':
    main()
