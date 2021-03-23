from datetime import datetime, date, timedelta

import pytest
import pytz


DATE = date(year=2020, month=3, day=23)

SWEDEN = 'Europe/Stockholm'
SWEDISH_TZ = pytz.timezone(SWEDEN)


AMSTERDAM = 'Europe/Amsterdam'
DUTCH_TZ = pytz.timezone(AMSTERDAM)
"""
Seems Swedish timezone is not uniquely affected :) -> https://stackoverflow.com/questions/7065164/how-to-make-an-unaware-datetime-timezone-aware-in-python#comment106636292_7065242
"putz(sic) has a bug that sets Amsterdam timezone to + 20 minutes to UTC, some archaic timezone from 1937. You had one job pytz. – Boris Feb 18 '20 at 16:09"
"""


@pytest.mark.parametrize('tz,expected_wrong_offset', [(DUTCH_TZ, 20), (SWEDISH_TZ, 72)])
def test_constructor_tzinfo(tz, expected_wrong_offset):
    """Test we erronously get an offset of 1 hour and 12 minutes when going from CET to UTC

    This seems to be due to one way setting tz as EDT(Eastern Daylight Time) and the other LMT (Local Mean Time)
    see https://stackoverflow.com/questions/23699115/datetime-with-pytz-timezone-different-offset-depending-on-how-tzinfo-is-set
    and works as mentioned in pytz docs:
    "Unfortunately using the tzinfo argument of the standard datetime constructors ‘’does not work’’ with pytz for
    many timezones."
    """
    dt = datetime(
        year=DATE.year, month=DATE.month, day=DATE.day, hour=0, minute=0, second=0, microsecond=0, tzinfo=tz
    )
    assert dt.tzinfo == tz
    assert dt.tzinfo.utcoffset(dt) == timedelta(minutes=expected_wrong_offset)
    dt = dt.astimezone(tz=pytz.utc)
    assert dt.tzinfo == pytz.utc
    assert dt.tzinfo.utcoffset(dt) == timedelta(minutes=0)
    dt = dt.astimezone(tz=tz)
    assert dt.tzinfo != tz  # because dt.tzinfo now is a EDT, while tz is LMT
    assert dt.tzinfo.utcoffset(dt) == timedelta(minutes=60)


@pytest.mark.parametrize('tz,expected_correct_offset', [(DUTCH_TZ, 60), (SWEDISH_TZ, 60)])
def test_localize(tz, expected_correct_offset):
    dt = datetime(
        year=DATE.year, month=DATE.month, day=DATE.day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None
    )
    dt = tz.localize(dt)
    assert dt.tzinfo != tz  # lolwat
    assert dt.tzinfo.utcoffset(dt) == timedelta(minutes=expected_correct_offset)
    # since localize can only run on tz unaware we continue with astimezone for the remainder of the test
    dt = dt.astimezone(tz=pytz.utc)
    assert dt.tzinfo == pytz.utc
    assert dt.tzinfo.utcoffset(dt) == timedelta(minutes=0)
    dt = dt.astimezone(tz=tz)
    assert dt.tzinfo != tz  # because dt.tzinfo now is a EDT, while tz is LMT
    assert dt.tzinfo.utcoffset(dt) == timedelta(minutes=60)


@pytest.mark.parametrize('tz,expected_correct_offset', [(DUTCH_TZ, 60), (SWEDISH_TZ, 60)])
def test_astimezone(tz, expected_correct_offset):
    dt = datetime(
        year=DATE.year, month=DATE.month, day=DATE.day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None
    )
    dt = dt.astimezone(tz)
    assert dt.tzinfo != tz  # sigh
    assert dt.tzinfo.utcoffset(dt) == timedelta(minutes=expected_correct_offset)
    dt = dt.astimezone(tz=pytz.utc)
    assert dt.tzinfo == pytz.utc
    assert dt.tzinfo.utcoffset(dt) == timedelta(minutes=0)
    dt = dt.astimezone(tz=tz)
    assert dt.tzinfo != tz  # because dt.tzinfo now is a EDT, while tz is LMT
    assert dt.tzinfo.utcoffset(dt) == timedelta(minutes=60)
