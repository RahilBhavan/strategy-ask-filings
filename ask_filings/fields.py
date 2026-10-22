"""Semantic names, units and accepted natural-language templates.

kind: 'flow' fields are period totals (a date inside a period selects that period);
'balance' fields are stated as of a date (period end or cover date).
"""
FIELDS = {
    'bitcoin holdings': {'kind': 'balance', 'field': 'btc_held', 'unit': 'BTC', 'table': 'weekly',
                         'intent': r'(?:bitcoin holdings|how much bitcoin did strategy hold)'},
    'bitcoin purchased': {'kind': 'flow', 'field': 'btc_acquired', 'unit': 'BTC', 'table': 'weekly',
                          'intent': r'(?:bitcoin purchased|how much bitcoin did strategy buy)'},
    'bitcoin purchase cost': {'kind': 'flow', 'field': 'btc_purchase_usd', 'unit': 'USD nominal', 'table': 'weekly',
                              'intent': r'(?:bitcoin purchase cost|how much did strategy spend on bitcoin)'},
    'usd reserve': {'kind': 'balance', 'field': 'usd_reserve', 'unit': 'USD nominal', 'table': 'weekly',
                    'intent': r'(?:usd reserve|what was the usd reserve)'},
    'usd cash': {'kind': 'balance', 'field': 'usd_cash', 'unit': 'USD nominal', 'table': 'weekly',
                 'intent': r'(?:usd cash|what was the usd cash)'},
    'basic shares': {'kind': 'balance', 'field': 'basic', 'unit': 'class A + class B shares', 'table': 'share_anchors',
                     'intent': r'(?:basic shares|how many basic shares were outstanding)'},
    'issuance': {'kind': 'flow', 'field': 'amount_usd', 'unit': 'net proceeds in stated currency', 'table': 'instrument_weekly',
                 'intent': r'(?:issuance|how much did strategy issue in) (?P<ticker>MSTR|STRC|STRD|STRF|STRK|STRE)'},
    'remaining capacity': {'kind': 'balance', 'field': 'available_usd', 'unit': 'stated currency', 'table': 'instrument_weekly',
                           'intent': r'(?:remaining capacity|how much capacity remained for) (?P<ticker>MSTR|STRC|STRD|STRF|STRK|STRE)'},
    'sats per basic share': {'kind': 'balance', 'field': 'sats_per_basic_share', 'unit': 'satoshis / basic share', 'table': 'weekly',
                             'intent': r'(?:sats per basic share|what were sats per basic share)',
                             'formula': 'btc_held * 100000000 / basic_shares (same-date weekly filed denominator only)'},
}
