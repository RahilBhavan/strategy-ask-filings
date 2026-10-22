import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
from ask_filings.dependency import PROJECT, LOCK

spec = importlib.util.spec_from_file_location('setup_ledger', PROJECT / 'scripts/setup_ledger.py')
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


class SetupTests(unittest.TestCase):
    def test_restore_repairs_and_repeats(self):
        # A full 55 MB extracted corpus belongs on disk, never RAM-backed /tmp.
        scratch = Path.home() / 'scratch/strategy-ask-filings'
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as tmp:
            root = Path(tmp)
            setup.restore(root)
            table = root / 'data/weekly.csv'
            original = table.read_bytes()
            table.write_bytes(b'interrupted or altered write')
            setup.restore(root)
            self.assertEqual(table.read_bytes(), original)
            for name, digest in LOCK['tables'].items():
                self.assertEqual(hashlib.sha256((root / 'data' / name).read_bytes()).hexdigest(), digest)

    def test_restore_refuses_symlink(self):
        scratch = Path.home() / 'scratch/strategy-ask-filings'
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as tmp:
            root = Path(tmp)
            (root / 'elsewhere').mkdir()
            (root / 'data').symlink_to(root / 'elsewhere', target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'symlink'):
                setup.restore(root)
            self.assertEqual(list((root / 'elsewhere').iterdir()), [])
