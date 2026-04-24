import pandas as pd

from mootdx.quotes import check_empty


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
