"""Checked offline CLI benchmark: python -m ask_filings.benchmark."""
import argparse
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from .dependency import LOCK, PROJECT, default_ledger


SUITE = PROJECT / 'benchmarks/cases.json'


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True,
                                    separators=(',', ':')).encode()).hexdigest()


def snapshot(result, root):
    """Keep all response metadata; fingerprint sections without copying SEC prose."""
    result = json.loads(json.dumps(result))
    for fact in result.get('facts', []):
        for citation in fact['evidence']:
            lines = citation.pop('lines')
            citation['lines_sha256'] = digest(lines)
            citation['line_numbers'] = [line['line'] for line in lines]
            source = Path(root) / 'data/raw' / '/'.join(citation['url'].split('/')[-2:])
            citation['local_bytes_sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
    return result


def differences(expected, actual, path='$'):
    """Return precise mismatch paths, including absent/extra facts and citations."""
    if type(expected) is not type(actual):
        return [path]
    if isinstance(expected, dict):
        return [p for key in sorted(expected.keys() | actual.keys())
                for p in ([path + '.' + key] if key not in expected or key not in actual
                          else differences(expected[key], actual[key], path + '.' + key))]
    if isinstance(expected, list):
        if len(expected) != len(actual):
            return [path + '.length']
        return [p for i, (a, b) in enumerate(zip(expected, actual))
                for p in differences(a, b, f'{path}[{i}]')]
    return [] if expected == actual else [path]


@contextmanager
def evidence_root(root, scenario):
    """Fault injection never mutates the configured checkout or bundled evidence."""
    if scenario == 'intact':
        yield root
        return
    if scenario not in ('missing_source', 'altered_source'):
        raise ValueError('unknown benchmark scenario: ' + scenario)
    scratch = Path.home() / 'scratch/strategy-ask-filings/benchmark'
    scratch.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(dir=scratch) as tmp:
            target = Path(tmp)
            shutil.copytree(Path(root) / 'ledger', target / 'ledger',
                            ignore=shutil.ignore_patterns('__pycache__'))
            (target / 'data/raw').mkdir(parents=True)
            for name in ('weekly.csv', 'instrument_weekly.csv', 'share_anchors.csv', 'raw/manifest.csv'):
                shutil.copyfile(Path(root) / 'data' / name, target / 'data' / name)
            if scenario == 'altered_source':
                # The fault cases ask the latest holdings question from this locked snapshot.
                rel = '000119312526424688/mstr-20261019.htm'
                dest = target / 'data/raw' / rel
                dest.parent.mkdir(parents=True)
                dest.write_bytes((Path(root) / 'data/raw' / rel).read_bytes() + b' altered')
            yield target
    finally:
        scratch.rmdir()


def evaluate(case, root, expected):
    with evidence_root(root, case.get('scenario', 'intact')) as selected:
        run = subprocess.run([sys.executable, '-m', 'ask_filings', case['question'],
                              '--ledger', str(selected), '--as-of', case['cutoff']],
                             cwd=PROJECT, capture_output=True, text=True, timeout=30)
        actual = {'exit_code': run.returncode,
                  'result': snapshot(json.loads(run.stdout), selected)}
    return differences(expected, actual)


def run_suite(root, suite=SUITE):
    suite = Path(suite)
    document = json.loads(suite.read_text())
    if document.get('version') != 1 or document.get('ledger_commit') != LOCK['commit']:
        raise ValueError('benchmark version or pinned ledger commit mismatch')
    cases = document['cases']
    if not cases or len({case['id'] for case in cases}) != len(cases):
        raise ValueError('benchmark requires nonempty cases with unique IDs')
    categories, intents, failures = {}, {}, []
    for case in cases:
        try:
            expected = json.loads((suite.parent / 'expected' / (case['expected'] + '.json')).read_text())
            paths = evaluate(case, root, expected)
        except (ValueError, OSError, subprocess.SubprocessError, KeyError) as exc:
            paths = ['execution: ' + str(exc)]
        for groups, label in ((categories, case['category']), (intents, case['intent'])):
            counts = groups.setdefault(label, {'passed': 0, 'failed': 0})
            counts['failed' if paths else 'passed'] += 1
        if paths:
            failures.append({'id': case['id'], 'question': case['question'], 'mismatches': paths})
    return {'ledger_commit': document['ledger_commit'],
            'suite_sha256': hashlib.sha256(suite.read_bytes()).hexdigest(),
            'cases': len(cases), 'passed': len(cases) - len(failures),
            'failed': len(failures), 'categories': categories, 'intents': intents,
            'failures': failures}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ledger', default=str(default_ledger()))
    parser.add_argument('--suite', type=Path, default=SUITE)
    args = parser.parse_args()
    try:
        report = run_suite(args.ledger, args.suite)
    except (ValueError, OSError, KeyError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report['failed'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
