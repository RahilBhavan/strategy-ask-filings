"""Exact intent routing with explicit refusals and dated source evidence."""
import datetime as dt
import importlib
from pathlib import Path
import re
import sys
from decimal import Decimal as D
from .fields import FIELDS


def iso(value):
    if not isinstance(value, str) or dt.date.fromisoformat(value).isoformat() != value:
        raise ValueError('date must be ISO YYYY-MM-DD')
    return value


def intent(query):
    if not isinstance(query, str) or len(query) > 500:
        raise ValueError('question must be text of at most 500 characters')
    for name, spec in FIELDS.items():
        pattern = spec['intent'] + r'(?: (?:on|for|at) (?P<date>\d{4}-\d{2}-\d{2}))?\??'
        match = re.fullmatch(pattern, query.strip(), re.I)
        if match:
            parts = match.groupdict()
            if parts.get('date'):
                iso(parts['date'])
            return name, spec, parts
    raise ValueError('unsupported or ambiguous question; use --fields for exact templates. '
                     'No unrestricted QA, forecasts, legal conclusions or dividend enactment inference.')


def ledger_api(root):
    root = Path(root).resolve()
    if not (root / 'ledger' / 'evidence.py').is_file():
        raise ValueError('adjacent strategy-8k-ledger with evidence module is required')
    existing = sys.modules.get('ledger')
    if existing and Path(existing.__file__).resolve().parent.parent != root:
        raise ValueError('a different ledger is already loaded; restart with one ledger path')
    sys.path.insert(0, str(root))
    build = importlib.import_module('ledger.build')
    evidence = importlib.import_module('ledger.evidence')
    return build, evidence


def answer(query, root, cutoff='2026-10-21'):
    iso(cutoff)
    name, spec, filters = intent(query)
    build, evidence = ledger_api(root)
    rows = build.read(spec['table'] + '.csv')
    rows = [r for r in rows if r['filed'] <= cutoff]
    date_field = 'as_of' if spec['table'] == 'share_anchors' else 'period_end'
    if filters.get('date'):
        rows = [r for r in rows if r[date_field] == filters['date']]
    if filters.get('ticker'):
        rows = [r for r in rows if r['ticker'] == filters['ticker'].upper() and r['action'] == 'atm_sale']
    if not rows:
        return {'status': 'unavailable', 'reason': 'no matching filed record by cutoff; dates are exact observation dates',
                'field': name, 'knowledge_cutoff': cutoff}
    latest = max(r[date_field] for r in rows)
    rows = [r for r in rows if r[date_field] == latest]
    # Amendments/multiple filings for one semantic identity require explicit resolution, never silent sum.
    identities = [(r.get('program'), r.get('ticker')) for r in rows]
    if len(set(identities)) != len(identities):
        return {'status': 'ambiguous', 'reason': 'multiple filings for one observation; inspect ledger accessions'}
    facts = []
    for row in rows:
        field = spec['field']
        if field == 'btc_purchase_usd' and D(row.get('btc_sold') or 0) > 0:
            return {'status': 'unavailable', 'field': name,
                    'reason': 'matching source field represents sale proceeds; no purchase-cost substitution'}
        if field == 'sats_per_basic_share':
            if not row['basic_shares'] or D(row['basic_shares']) <= 0:
                return {'status': 'unavailable', 'field': name,
                        'reason': 'no same-date filed basic-share denominator; no model substitution'}
            value = format(D(row['btc_held']) * 100000000 / D(row['basic_shares']), 'f')
            citations = [evidence.cite(row, k) for k in ('btc_held', 'basic_shares')]
        else:
            if not row.get(field):
                return {'status': 'unavailable', 'field': name, 'reason': 'field not disclosed in matching record'}
            value = row[field]
            citations = [evidence.cite(row, field)]
        facts.append({'value': value, 'unit': spec['unit'], 'as_of': row[date_field],
                      'period_start': row.get('period_start'), 'filed': row['filed'],
                      'program': row.get('program'), 'currency': row.get('currency'),
                      'formula': spec.get('formula'), 'evidence': citations})
    return {'status': 'answered', 'engine': 'deterministic exact supported intents; no LLM',
            'field': name, 'knowledge_cutoff': cutoff, 'facts': facts,
            'uncertainty': 'As filed, rounded figures; source lines are normalized source sections, not original HTML lines. '
                           'Latest means latest in the frozen corpus by cutoff, not a live completeness claim.'}
