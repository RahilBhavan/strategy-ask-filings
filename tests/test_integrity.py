import json
import subprocess
import sys
import shutil
import tempfile
from pathlib import Path
import unittest
from ask_filings.dependency import verify_table


class IntegrityTests(unittest.TestCase):
    def scratch(self):
        root = Path.home() / 'scratch/strategy-ask-filings'
        root.mkdir(parents=True, exist_ok=True)
        return tempfile.TemporaryDirectory(dir=root)

    def test_altered_table_refused(self):
        from test_ask import LEDGER
        with self.scratch() as tmp:
            root = Path(tmp)
            (root / 'data').mkdir()
            table = root / 'data/weekly.csv'
            shutil.copyfile(LEDGER / 'data/weekly.csv', table)
            table.write_bytes(table.read_bytes().replace(b'848517', b'123'))
            shutil.copytree(LEDGER / 'ledger', root / 'ledger', ignore=shutil.ignore_patterns('__pycache__'))
            run = subprocess.run([sys.executable, '-m', 'ask_filings', 'bitcoin holdings',
                                  '--ledger', str(root)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertIn('table hash mismatch', json.loads(run.stdout)['reason'])
            with self.assertRaisesRegex(ValueError, 'table hash mismatch'):
                verify_table(root, 'weekly.csv')

    def test_missing_source_is_offline_refusal(self):
        from test_ask import LEDGER
        with self.scratch() as tmp:
            root = Path(tmp)
            shutil.copytree(LEDGER / 'ledger', root / 'ledger', ignore=shutil.ignore_patterns('__pycache__'))
            (root / 'data').mkdir()
            shutil.copyfile(LEDGER / 'data/weekly.csv', root / 'data/weekly.csv')
            run = subprocess.run([sys.executable, '-m', 'ask_filings', 'bitcoin holdings',
                                  '--ledger', str(root)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertIn('source cache missing', json.loads(run.stdout)['reason'])

    def test_altered_source_refused(self):
        from test_ask import LEDGER
        import csv
        with self.scratch() as tmp:
            root = Path(tmp)
            shutil.copytree(LEDGER / 'ledger', root / 'ledger', ignore=shutil.ignore_patterns('__pycache__'))
            (root / 'data/raw').mkdir(parents=True)
            shutil.copyfile(LEDGER / 'data/weekly.csv', root / 'data/weekly.csv')
            shutil.copyfile(LEDGER / 'data/raw/manifest.csv', root / 'data/raw/manifest.csv')
            with (root / 'data/weekly.csv').open() as f:
                rows = list(csv.DictReader(f))
            row = next(r for r in rows if r['period_end'] == '2026-10-18')
            rel = '/'.join(row['doc_url'].split('/')[-2:])
            target = root / 'data/raw' / rel
            target.parent.mkdir(parents=True)
            target.write_bytes((LEDGER / 'data/raw' / rel).read_bytes() + b' altered')
            run = subprocess.run([sys.executable, '-m', 'ask_filings', 'bitcoin holdings',
                                  '--ledger', str(root)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertIn('hash', json.loads(run.stdout)['reason'])

    def test_altered_manifest_refused(self):
        from test_ask import LEDGER
        import csv
        import hashlib
        with self.scratch() as tmp:
            root = Path(tmp)
            shutil.copytree(LEDGER / 'ledger', root / 'ledger', ignore=shutil.ignore_patterns('__pycache__'))
            (root / 'data/raw').mkdir(parents=True)
            shutil.copyfile(LEDGER / 'data/weekly.csv', root / 'data/weekly.csv')
            with (root / 'data/weekly.csv').open() as f:
                row = next(r for r in csv.DictReader(f) if r['period_end'] == '2026-10-18')
            rel = '/'.join(row['doc_url'].split('/')[-2:])
            target = root / 'data/raw' / rel
            target.parent.mkdir(parents=True)
            original = (LEDGER / 'data/raw' / rel).read_bytes()
            changed = original + b' altered'
            target.write_bytes(changed)
            manifest = (LEDGER / 'data/raw/manifest.csv').read_text()
            manifest = manifest.replace(hashlib.sha256(original).hexdigest(), hashlib.sha256(changed).hexdigest())
            (root / 'data/raw/manifest.csv').write_text(manifest)
            run = subprocess.run([sys.executable, '-m', 'ask_filings', 'bitcoin holdings',
                                  '--ledger', str(root)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertIn('manifest hash mismatch', json.loads(run.stdout)['reason'])
