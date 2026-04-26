import pandas as pd
import pytest
from tenacity import wait_none

from mootdx.exceptions import MootdxException
from mootdx.quotes import ExtQuotes
from mootdx.quotes import StdQuotes
from mootdx.quotes import check_empty


class EmptyStdBarsClient:
    def __init__(self):
        self.calls = 0

    def get_security_bars(self, *args):
        self.calls += 1
        return []


class EmptyExtBarsClient:
    def __init__(self):
        self.calls = 0

    def get_instrument_bars(self, **kwargs):
        self.calls += 1
        return []


def disable_ext_bars_retry_wait():
    for method_name in ('bars', '_bars_retry'):
        method = getattr(ExtQuotes, method_name, None)
        if method is not None and hasattr(method, 'retry'):
            method.retry.wait = wait_none()


def test_std_bars_skip_retry_raises_on_empty_result_without_retrying():
    client = EmptyStdBarsClient()
    quotes = StdQuotes.__new__(StdQuotes)
    quotes.client = client

    with pytest.raises(MootdxException, match='bars 返回数据空'):
        quotes.bars(symbol='600036', skip_retry=True)

    assert client.calls == 1


def test_ext_bars_skip_retry_raises_on_empty_result_without_retrying():
    disable_ext_bars_retry_wait()
    client = EmptyExtBarsClient()
    quotes = ExtQuotes.__new__(ExtQuotes)
    quotes.client = client

    with pytest.raises(MootdxException, match='bars 返回数据空'):
        quotes.bars(frequency=9, market=47, symbol='IF2605', skip_retry=True)

    assert client.calls == 1


def test_ext_bars_default_retries_empty_result_three_times():
    disable_ext_bars_retry_wait()
    client = EmptyExtBarsClient()
    quotes = ExtQuotes.__new__(ExtQuotes)
    quotes.client = client

    result = quotes.bars(frequency=9, market=47, symbol='IF2605')

    assert result.empty is True
    assert client.calls == 3


def test_check_empty_handles_non_empty_datetime_frame():
    data = pd.DataFrame(
        {
            'datetime': pd.to_datetime(['2026-04-24 09:30:00']),
            'price': [2.03],
        }
    )

    assert check_empty(data) is False


def test_check_empty_handles_empty_frame():
    assert check_empty(pd.DataFrame()) is True
