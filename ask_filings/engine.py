"""Intent routing with explicit refusals and dated source evidence.

A date selects the observation filed for that date. A date inside a weekly reporting
period selects that period for period totals and says so; balances are filed only as
of period end, so a mid-period balance refuses and names the period end to ask about.
"""
import datetime as dt
import importlib
from pathlib import Path
import re
import sys
from decimal import Decimal as D
from .fields import FIELDS
from .dependency import verify_table, verify_manifest

DATE = r'\d{4}-\d{2}-\d{2}'
PREFIX = r'(?:(?:what (?:were|was|are|is) )?(?P<latest>(?:the )?latest) )?'
SUFFIX = (rf'(?: (?:(?:on|for|at|as of) (?P<date>{DATE})'
          rf'|(?:(?:for|in|during) )?(?:the )?week (?:of|containing) (?P<week>{DATE})'
          rf'|(?:between|from) (?P<start>{DATE}) (?:and|to|through) (?P<end>{DATE})))?\??')
MNAV = ('mNAV is unsupported: it divides market value (MSTR share price, or enterprise value) by '
        'bitcoin NAV (bitcoin price x holdings). Market prices are not stated in these SEC filings, '
        'and this tool answers only filed values. Holdings are available: try "bitcoin holdings".')
UNSUPPORTED = ('unsupported or ambiguous question; use --fields for exact templates. '
               'No unrestricted QA, forecasts, legal conclusions or dividend enactment inference.')
NO_RECORD = 'no matching filed record by cutoff'


def iso(value):
    try:
        if not isinstance(value, str) or dt.date.fromisoformat(value).isoformat() != value:
            raise ValueError
    except ValueError:
        raise ValueError('date must be ISO YYYY-MM-DD') from None
    return value


def intent(query):
    if not isinstance(query, str) or len(query) > 500:
        raise ValueError('question must be text of at most 500 characters')
    text = ' '.join(query.split())
    if re.search(r'\bmnav\b', text, re.I):
        raise ValueError(MNAV)
    for name, spec in FIELDS.items():
        match = re.fullmatch(PREFIX + spec['intent'] + SUFFIX, text, re.I)
        if match:
            parts = match.groupdict()
            for key in ('date', 'week', 'start', 'end'):
                if parts.get(key):
                    iso(parts[key])
            if parts.get('latest') and any(parts.get(k) for k in ('date', 'week', 'start')):
                raise ValueError('use either "latest" or a date, not both')
            if parts.get('start') and parts['start'] > parts['end']:
                raise ValueError('range start must be on or before its end')
            return name, spec, parts
    raise ValueError(UNSUPPORTED)


def ledger_api(root):
    root = Path(root).resolve()
    if not (root / 'ledger' / 'evidence.py').is_file():
        raise ValueError('pinned strategy-8k-ledger with evidence module is required; run scripts/setup_ledger.py')
    existing = sys.modules.get('ledger')
    if existing and Path(existing.__file__).resolve().parent.parent != root:
        raise ValueError('a different ledger is already loaded; restart with one ledger path')
    sys.path.insert(0, str(root))
    build = importlib.import_module('ledger.build')
    evidence = importlib.import_module('ledger.evidence')
    return build, evidence


def unit(spec, row):
    """Name the currency when the row states one (all current rows are USD)."""
    currency = row.get('currency')
    if spec['table'] != 'instrument_weekly' or not currency:
        return spec['unit']
    return f'{currency} net proceeds' if spec['field'] == 'amount_usd' else currency


def nearest(day, dates):
    dates = sorted(set(dates))
    near = [d for d in dates if d < day][-1:] + [d for d in dates if d > day][:1]
    return ' or '.join(near) if near else 'none'


def unavailable(name, cutoff, reason):
    """Record-selection miss; cutoff is None for a matched record lacking the field."""
    result = {'status': 'unavailable', 'reason': reason, 'field': name}
    if cutoff:
        result['knowledge_cutoff'] = cutoff
    return result


def select(name, spec, filters, rows, cutoff):
    """Return (rows, note) or an unavailable result for date/week/range filters."""
    shares = spec['table'] == 'share_anchors'
    date_field = 'as_of' if shares else 'period_end'
    day = filters.get('date') or filters.get('week')
    if filters.get('start'):
        lo, hi = filters['start'], filters['end']
        if shares:
            inside = [r for r in rows if lo <= r['as_of'] <= hi]
            partial = []
        else:
            inside = [r for r in rows if lo <= r['period_start'] and r['period_end'] <= hi]
            partial = sorted({f"{r['period_start']} to {r['period_end']}" for r in rows
                              if r not in inside and r['period_start'] <= hi and r['period_end'] >= lo})
        if not inside:
            return unavailable(name, cutoff, f'{NO_RECORD} inside {lo} to {hi}'
                               + (f'; partly overlapping periods: {", ".join(partial)}' if partial else ''))
        note = (f'{len({r[date_field] for r in inside})} filed observations inside {lo} to {hi}. '
                'Weeks without a weekly filing are absent, not zero.')
        if partial:
            note += ' Excluded periods that only partly overlap the range: ' + ', '.join(partial) + '.'
        return inside, note
    if not day:
        return rows, None
    exact = [r for r in rows if r[date_field] == day]
    if exact and not filters.get('week'):
        return exact, None
    if shares:
        return unavailable(name, cutoff, f'{NO_RECORD}; basic shares are filed as of quarterly/annual cover '
                           f'dates, nearest: {nearest(day, [r["as_of"] for r in rows])}')
    containing = [r for r in rows if r['period_start'] <= day <= r['period_end']]
    if not containing:
        return unavailable(name, cutoff, f'{NO_RECORD}; no filed reporting period contains {day}; '
                           f'nearest period ends: {nearest(day, [r["period_end"] for r in rows])}')
    start, end = containing[0]['period_start'], containing[0]['period_end']
    period = f'{day} is inside reporting period {start} to {end}'
    if filters.get('week'):
        detail = 'the filing reports the period total' if spec['kind'] == 'flow' else \
            f'the balance is as of the period end, {end}'
        return containing, f'week of {day}: reporting period {start} to {end}; {detail}.'
    if spec['kind'] == 'balance':
        return unavailable(name, cutoff, f'{period}; balances are filed only as of period end. '
                           f'Ask "{name} on {end}" or "{name} week of {day}".')
    return containing, f'{period}; the filing reports the period total, not a daily figure.'


def answer(query, root, cutoff='2026-10-21'):
    iso(cutoff)
    name, spec, filters = intent(query)
    build, evidence = ledger_api(root)
    verify_table(root, spec['table'] + '.csv')
    rows = build.read(spec['table'] + '.csv')
    rows = [r for r in rows if r['filed'] <= cutoff]
    date_field = 'as_of' if spec['table'] == 'share_anchors' else 'period_end'
    if filters.get('ticker'):
        rows = [r for r in rows if r['ticker'] == filters['ticker'].upper() and r['action'] == 'atm_sale']
    if not rows:
        return unavailable(name, cutoff, NO_RECORD)
    selected = select(name, spec, filters, rows, cutoff)
    if isinstance(selected, dict):
        return selected
    rows, note = selected
    if not filters.get('start'):
        latest = max(r[date_field] for r in rows)
        rows = [r for r in rows if r[date_field] == latest]
    # Amendments/multiple filings for one semantic identity require explicit resolution, never silent sum.
    identities = [(r[date_field], r.get('program'), r.get('ticker')) for r in rows]
    if len(set(identities)) != len(identities):
        return {'status': 'ambiguous', 'reason': 'multiple filings for one observation; inspect ledger accessions'}
    facts, missing = [], []
    for row in rows:
        # Asking never hydrates or contacts SEC; setup restores the frozen cache.
        if not Path(evidence.edgar.cache_path(row['doc_url'])).is_file():
            raise ValueError('source cache missing; run scripts/setup_ledger.py')
        verify_manifest(root)
        field = spec['field']
        if field == 'btc_purchase_usd' and D(row.get('btc_sold') or 0) > 0:
            return unavailable(name, None, 'matching source field represents sale proceeds; no purchase-cost '
                               'substitution' + (f' (period ending {row[date_field]})' if filters.get('start') else ''))
        if field == 'sats_per_basic_share':
            if not row['basic_shares'] or D(row['basic_shares']) <= 0:
                if filters.get('start'):
                    missing.append(row[date_field])
                    continue
                return unavailable(name, None, 'no same-date filed basic-share denominator; no model substitution')
            value = format(D(row['btc_held']) * 100000000 / D(row['basic_shares']), 'f')
            citations = [evidence.cite(row, k) for k in ('btc_held', 'basic_shares')]
        else:
            if not row.get(field):
                if filters.get('start'):
                    missing.append(row[date_field])
                    continue
                return unavailable(name, None, 'field not disclosed in matching record')
            value = row[field]
            citations = [evidence.cite(row, field)]
        facts.append({'value': value, 'unit': unit(spec, row), 'as_of': row[date_field],
                      'period_start': row.get('period_start'), 'filed': row['filed'],
                      'program': row.get('program'), 'currency': row.get('currency'),
                      'formula': spec.get('formula'), 'evidence': citations})
    if not facts:
        return unavailable(name, None, 'field not disclosed in any matching record')
    result = {'status': 'answered', 'engine': 'deterministic exact supported intents; no LLM',
              'field': name, 'knowledge_cutoff': cutoff, 'facts': facts,
              'uncertainty': 'As filed, rounded figures; source lines are normalized source sections, not original HTML lines. '
                             'Latest means latest in the frozen corpus by cutoff, not a live completeness claim.'}
    if missing:
        note += ' Not disclosed, so excluded' + (' and no total is given' if spec['kind'] == 'flow' else '') + ': ' + ', '.join(missing) + '.'
    if note:
        result['note'] = note
    if filters.get('start') and spec['kind'] == 'flow' and not missing and len({f['unit'] for f in facts}) == 1:
        result['total'] = {'value': format(sum(D(f['value']) for f in facts), 'f'), 'unit': facts[0]['unit'],
                           'formula': f'sum of the {len(facts)} filed values listed in facts'}
    return result
