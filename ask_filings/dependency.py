"""Frozen ledger v1 table contract and portable checkout location."""
import hashlib
import json
import os
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
LOCK = json.loads((PROJECT / 'fixtures/ledger-lock.json').read_text())


def work_dir():
    """Disk-backed working area: git-ignored `.ask-filings/` in this repo, or ASK_FILINGS_HOME."""
    return Path(os.environ.get('ASK_FILINGS_HOME') or PROJECT / '.ask-filings')


def scratch_dir():
    path = work_dir() / 'scratch'
    path.mkdir(parents=True, exist_ok=True)
    return path


def default_ledger():
    return Path(os.environ.get('ASK_FILINGS_LEDGER') or work_dir() / ('ledger-' + LOCK['commit']))


def verify_table(root, name):
    path = Path(root) / 'data' / name
    if hashlib.sha256(path.read_bytes()).hexdigest() != LOCK['tables'][name]:
        raise ValueError('frozen ledger table hash mismatch; run scripts/setup_ledger.py')


def verify_manifest(root):
    path = Path(root) / 'data/raw/manifest.csv'
    if hashlib.sha256(path.read_bytes()).hexdigest() != LOCK['source_manifest_sha256']:
        raise ValueError('frozen source manifest hash mismatch; run scripts/setup_ledger.py')
