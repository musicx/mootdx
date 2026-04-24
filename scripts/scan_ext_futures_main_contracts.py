from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

from mootdx.consts import KLINE_DAILY
from mootdx.consts import KLINE_1MIN
from mootdx.quotes import Quotes
from mootdx.utils import to_data


MARKETS = {
    28: '郑州商品',
    29: '大连商品',
    30: '上海期货',
    47: '中金所期货',
    66: '广州期货',
}

DAILY_UPPER_BOUND = {
    28: 5000,
    29: 5000,
    30: 5000,
    47: 5000,
    66: 2000,
}

M1_UPPER_BOUND = {
    28: 370000,
    29: 370000,
    30: 370000,
    47: 370000,
    66: 150000,
}


def fetch_main_contracts(client: Quotes) -> pd.DataFrame:
    chunks = []
    count = client.instrument_count()

    for start in range(0, count, 1000):
        frame = client.instrument(start, 1000)
        frame = frame[frame['market'].isin(MARKETS)][['market', 'code', 'name']]
        frame = frame[frame['name'].str.contains('主连', na=False)]

        if not frame.empty:
            chunks.append(frame)

    result = pd.concat(chunks, ignore_index=True).drop_duplicates().sort_values(['market', 'code']).reset_index(drop=True)
    result['market_name'] = result['market'].map(MARKETS)
    return result[['market', 'market_name', 'code', 'name']]


def fetch_bars_raw(client: Quotes, frequency: int, market: int, code: str, start: int, count: int = 800) -> pd.DataFrame:
    raw = client.client.get_instrument_bars(category=frequency, market=market, code=code, start=start, count=count)
    return to_data(raw)


def find_earliest_timestamp(client: Quotes, frequency: int, market: int, code: str, upper_bound: int) -> str:
    low = 0
    high = upper_bound
    best = None

    while low <= high:
        middle = (low + high) // 2
        frame = fetch_bars_raw(client, frequency, market, code, middle)

        if frame.empty:
            high = middle - 1
            continue

        best = frame
        low = middle + 1

    if best is None or best.empty:
        return ''

    return str(best.index.min())


def fields_to_text(frame: pd.DataFrame) -> str:
    return ', '.join(frame.columns)


def render_markdown(rows: list[dict[str, str]]) -> str:
    lines = [
        '## 中国期货主连合约全量扫描清单',
        '',
        '> 生成方式: `python scripts/scan_ext_futures_main_contracts.py`',
        '> 生成时间: 2026-04-24',
        '',
        '说明:',
        '',
        '- 范围为扩展行情当前可见的五个中国期货市场主连合约',
        '- `daily_earliest` 为日线最早可回溯时间',
        '- `m1_earliest` 为 1 分钟 K 线最早可回溯时间',
        '- `quote_fields`、`minute_fields`、`bars_fields` 为实测返回字段',
        '',
        '| market | market_name | code | name | daily_earliest | m1_earliest | quote_fields | minute_fields | bars_fields |',
        '| --- | --- | --- | --- | --- | --- | --- | --- | --- |',
    ]

    for row in rows:
        lines.append(
            '| {market} | {market_name} | {code} | {name} | {daily_earliest} | {m1_earliest} | {quote_fields} | {minute_fields} | {bars_fields} |'.format(
                **row
            )
        )

    lines.append('')
    return '\n'.join(lines)


def main() -> None:
    client = Quotes.factory('ext', timeout=5)
    contracts = fetch_main_contracts(client)
    rows = []

    for record in contracts.itertuples(index=False):
        quote = client.quote(record.market, record.code)
        minute = client.minute(record.market, record.code)
        daily = fetch_bars_raw(client, KLINE_DAILY, record.market, record.code, 0, 3)
        minute_bar = fetch_bars_raw(client, KLINE_1MIN, record.market, record.code, 0, 3)

        rows.append(
            {
                'market': str(record.market),
                'market_name': record.market_name,
                'code': record.code,
                'name': record.name,
                'daily_earliest': find_earliest_timestamp(
                    client, KLINE_DAILY, record.market, record.code, DAILY_UPPER_BOUND[record.market]
                ),
                'm1_earliest': find_earliest_timestamp(
                    client, KLINE_1MIN, record.market, record.code, M1_UPPER_BOUND[record.market]
                ),
                'quote_fields': fields_to_text(quote),
                'minute_fields': fields_to_text(minute),
                'bars_fields': fields_to_text(daily if not daily.empty else minute_bar),
            }
        )

    docs_dir = Path(__file__).resolve().parents[1] / 'docs' / 'api'
    csv_path = docs_dir / 'quote2_futures_scan.csv'
    md_path = docs_dir / 'quote2_futures_scan.md'

    with csv_path.open('w', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                'market',
                'market_name',
                'code',
                'name',
                'daily_earliest',
                'm1_earliest',
                'quote_fields',
                'minute_fields',
                'bars_fields',
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    md_path.write_text(render_markdown(rows), encoding='utf-8')


if __name__ == '__main__':
    main()
