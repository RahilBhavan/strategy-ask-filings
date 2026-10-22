"""Plain-text answer: one answer line first, then notes and evidence. --json keeps the full result."""
from decimal import Decimal as D
from .fields import FIELDS


def amount(value, unit):
    v = D(value)
    text = f'{v:,.2f}' if v != v.to_integral() else f'{int(v):,}'
    rounded = ' (rounded for display; exact in --json)' if D(text.replace(',', '')) != v else ''
    if unit.startswith('USD'):
        rest = unit[3:].strip(' ,')
        return f'${text}' + (f' ({rest})' if rest and rest != 'nominal' else '') + rounded
    return f'{text} {unit}{rounded}'


def when(name, fact):
    if FIELDS[name]['kind'] == 'flow':
        return f"in period {fact['period_start']} to {fact['as_of']}"
    period = f" (period {fact['period_start']} to {fact['as_of']})" if fact['period_start'] else ''
    return f"as of {fact['as_of']}{period}"


def fact_line(name, fact):
    program = f" ({fact['program']})" if fact.get('program') else ''
    return f"{name}{program}: {amount(fact['value'], fact['unit'])}, {when(name, fact)}, filed {fact['filed']}"


def lines_range(numbers):
    spans, start = [], None
    for i, n in enumerate(numbers):
        start = n if start is None else start
        if i + 1 == len(numbers) or numbers[i + 1] != n + 1:
            spans.append(str(start) if start == n else f'{start}-{n}')
            start = None
    return ', '.join(spans)


def evidence(cite, full):
    out = [f"  {cite['field']} from {cite['url']}",
           f"    accession {cite['accession']}, filed {cite['filed']}, sha256 {cite['sha256'][:12]}...",
           f"    normalized lines {lines_range([l['line'] for l in cite['lines']])}"]
    if full:
        out += [f"    {l['line']:>4}: {l['text'][:160]}" for l in cite['lines']]
    return out


def text(result):
    status = result['status']
    if status != 'answered':
        return f"{status.capitalize()}: {result['reason']}"
    name, facts = result['field'], result['facts']
    total = result.get('total')
    if total:
        first = f"Answer: {name} total {amount(total['value'], total['unit'])} ({total['formula']})"
    elif len(facts) == 1:
        first = 'Answer: ' + fact_line(name, facts[0])
    else:
        first = f'Answer: {len(facts)} separate {name} values (not summed):'
    out = [first]
    if total or len(facts) > 1:
        out += ['  ' + fact_line(name, f) for f in facts]
    if result.get('note'):
        out.append('Note: ' + result['note'])
    if any(f['formula'] for f in facts):
        out.append('Formula: ' + facts[0]['formula'])
    out.append('Evidence:')
    for fact in facts:
        for cite in fact['evidence']:
            out += evidence(cite, full=len(facts) == 1)
    out += ['Limits: ' + result['uncertainty'], 'Full JSON (all source lines and hashes): add --json.']
    return '\n'.join(out)
