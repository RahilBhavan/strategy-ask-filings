import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
from ask_filings.dependency import PROJECT, LOCK, scratch_dir

spec = importlib.util.spec_from_file_location('setup_ledger', PROJECT / 'scripts/setup_ledger.py')
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


class SetupTests(unittest.TestCase):
    def test_restore_repairs_and_repeats(self):
        # A full 55 MB extracted corpus belongs on disk (the repo work dir), never RAM-backed /tmp.
        with tempfile.TemporaryDirectory(dir=scratch_dir()) as tmp:
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
        with tempfile.TemporaryDirectory(dir=scratch_dir()) as tmp:
            root = Path(tmp)
            (root / 'elsewhere').mkdir()
            (root / 'data').symlink_to(root / 'elsewhere', target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'symlink'):
                setup.restore(root)
            self.assertEqual(list((root / 'elsewhere').iterdir()), [])

    def test_default_work_dir_is_ignored_repo_path_with_overrides(self):
        import os, subprocess
        from unittest.mock import patch
        from ask_filings.dependency import default_ledger, work_dir
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop('ASK_FILINGS_HOME', None)
            os.environ.pop('ASK_FILINGS_LEDGER', None)
            self.assertEqual(default_ledger(), PROJECT / '.ask-filings' / ('ledger-' + LOCK['commit']))
            ignored = subprocess.run(['git', 'check-ignore', '-q', str(work_dir() / 'x')], cwd=PROJECT)
            self.assertEqual(ignored.returncode, 0)
            os.environ['ASK_FILINGS_HOME'] = '/data/ask'
            self.assertEqual(default_ledger(), Path('/data/ask/ledger-' + LOCK['commit']))
            os.environ['ASK_FILINGS_LEDGER'] = '/data/custom'
            self.assertEqual(default_ledger(), Path('/data/custom'))

