import pytest
from src.validators import validate_word_timings

def test_valid_timing_data():
    words=[{"word":"hello","start":0.1,"end":0.4},{"word":"world","start":0.5,"end":0.9}]
    assert validate_word_timings(words,2)==1.0

def test_rejects_missing_timestamp():
    with pytest.raises(ValueError):
        validate_word_timings([{"word":"hello","start":0.1}],1)

def test_rejects_non_chronological_words():
    with pytest.raises(ValueError):
        validate_word_timings([{"word":"later","start":2,"end":3},{"word":"earlier","start":1,"end":1.5}],2)

def test_rejects_low_coverage():
    with pytest.raises(ValueError):
        validate_word_timings([{"word":"hello","start":0,"end":1}],3)
