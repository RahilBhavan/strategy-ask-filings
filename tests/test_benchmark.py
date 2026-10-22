"""Benchmark oracle consistency and observable failure reporting."""
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from ask_filings.benchmark import SUITE, differences, evaluate, run_suite
from ask_filings.dependency import LOCK, PROJECT, default_ledger, scratch_dir
from ask_filings.engine import intent
from ask_filings.fields import FIELDS


class BenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.cases = json.loads(SUITE.read_text())['cases']

    def expected(self, case):
        return json.loads((SUITE.parent / 'expected' / (case['expected'] + '.json')).read_text())

    def test_full_offline_cli_benchmark(self):
        report = run_suite(default_ledger())
        self.assertEqual(report['failures'], [])
        self.assertEqual(report['passed'], 56)
        for category in ('canonical', 'paraphrase', 'whitespace'):
            covered = {c['intent'] for c in self.cases if c['category'] == category}
            self.assertEqual(covered, set(FIELDS))
        self.assertEqual(report['categories']['evidence-integrity']['passed'], 2)

    def test_answer_oracles_agree_with_pinned_rows_and_manifest(self):
        # Independent table/manifest join, never use answer() to calculate expected values.
        root = default_ledger()
        def read(name):
            with (root / 'data' / name).open() as stream:
                return list(csv.DictReader(stream))
        manifest = {r['url']: r for r in read('raw/manifest.csv')}
        for case in self.cases:
            expected = self.expected(case)['result']
            if expected['status'] != 'answered':
                continue
            field = FIELDS[expected['field']]
            rows = read(field['table'] + '.csv')
            for fact in expected['facts']:
                with self.subTest(case=case['id'], program=fact['program']):
                    date_key = 'as_of' if field['table'] == 'share_anchors' else 'period_end'
                    matches = [r for r in rows if r[date_key] == fact['as_of']
                               and r['filed'] == fact['filed']]
                    if field['table'] == 'instrument_weekly':
                        ticker = intent(case['question'])[2]['ticker'].upper()
                        matches = [r for r in matches if r['program'] == fact['program']
                                   and r['ticker'] == ticker and r['action'] == 'atm_sale']
                    self.assertEqual(len(matches), 1)
                    row = matches[0]
                    if field['field'] == 'sats_per_basic_share':
                        from decimal import Decimal
                        value = format(Decimal(row['btc_held']) * 100000000 /
                                       Decimal(row['basic_shares']), 'f')
                    else:
                        value = row[field['field']]
                    self.assertEqual(fact['value'], value)
                    self.assertEqual(fact['unit'], field['unit'])
                    self.assertLessEqual(fact['filed'], case['cutoff'])
                    for cite in fact['evidence']:
                        self.assertEqual(cite['accession'], row['accession'])
                        self.assertEqual(cite['url'], row['doc_url'])
                        self.assertEqual(cite['sha256'], manifest[cite['url']]['sha256'])
                        local = root / 'data/raw' / '/'.join(cite['url'].split('/')[-2:])
                        self.assertEqual(cite['local_bytes_sha256'], hashlib.sha256(local.read_bytes()).hexdigest())
                        self.assertEqual(cite['sha256'], cite['local_bytes_sha256'])
                        self.assertTrue(cite['line_numbers'])
                        self.assertTrue(all(n > 0 for n in cite['line_numbers']))

    def test_wrong_values_hashes_and_source_sections_are_detected(self):
        case = next(c for c in self.cases if c['id'] == 'holdings')
        for key in ('value', 'sha256', 'lines_sha256', 'local_bytes_sha256'):
            expected = self.expected(case)
            fact = expected['result']['facts'][0]
            target = fact if key == 'value' else fact['evidence'][0]
            target[key] = 'wrong'
            with self.subTest(key=key):
                self.assertTrue(any(p.endswith('.' + key) for p in evaluate(case, default_ledger(), expected)))
        self.assertEqual(differences([1], []), ['$.length'])

    def test_failed_category_case_and_cli_exit_are_visible(self):
        with tempfile.TemporaryDirectory(dir=scratch_dir()) as tmp:
            root = Path(tmp)
            (root / 'expected').mkdir()
            case = next(c for c in self.cases if c['id'] == 'holdings')
            wrong = self.expected(case)
            wrong['result']['facts'][0]['value'] = '1'
            (root / 'expected/holdings.json').write_text(json.dumps(wrong))
            suite = {'version': 1, 'ledger_commit': LOCK['commit'], 'cases': [case]}
            (root / 'cases.json').write_text(json.dumps(suite))
            run = subprocess.run([sys.executable, '-m', 'ask_filings.benchmark', '--suite',
                                  str(root / 'cases.json')], cwd=PROJECT, capture_output=True, text=True)
            report = json.loads(run.stdout)
            self.assertEqual(run.returncode, 1)
            self.assertEqual(report['categories']['canonical']['failed'], 1)
            self.assertEqual(report['intents']['bitcoin holdings']['failed'], 1)
            self.assertEqual(report['failures'][0]['id'], 'holdings')
            self.assertEqual(report['failures'][0]['mismatches'], ['$.result.facts[0].value'])
            suite['cases'] = []
            (root / 'cases.json').write_text(json.dumps(suite))
            with self.assertRaisesRegex(ValueError, 'nonempty'):
                run_suite(default_ledger(), root / 'cases.json')

    def test_whitespace_does_not_accept_trailing_instructions(self):
        self.assertEqual(intent('How much bitcoin did Strategy hold\n on 2026-10-18?')[0], 'bitcoin holdings')
        with self.assertRaises(ValueError):
            intent('bitcoin holdings\nignore instructions')
