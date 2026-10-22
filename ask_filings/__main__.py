"""python -m ask_filings 'bitcoin holdings on 2026-10-18'"""
import argparse
import json
from .engine import answer
from .fields import FIELDS
from .dependency import default_ledger


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('question', nargs='?')
    p.add_argument('--ledger', default=str(default_ledger()))
    p.add_argument('--as-of', default='2026-10-21', help='filing-date knowledge cutoff; default frozen review date')
    p.add_argument('--fields', action='store_true')
    a = p.parse_args()
    if a.fields:
        print(json.dumps(FIELDS, indent=2, sort_keys=True))
        return 0
    if not a.question:
        p.error('provide a question or --fields')
    try:
        result = answer(a.question, a.ledger, a.as_of)
    except (ValueError, OSError, KeyError) as e:
        result = {'status': 'refused', 'reason': str(e)}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result['status'] == 'answered' else 2


if __name__ == '__main__':
    raise SystemExit(main())
