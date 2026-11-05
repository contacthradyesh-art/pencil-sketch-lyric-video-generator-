"""Shared validation helpers for lyric timing data."""
import math
def validate_word_timings(words, expected_count=None, min_coverage=0.98):
    if not isinstance(words,list) or not words: raise ValueError("No aligned words were returned.")
    previous_start=-1.0
    for index,item in enumerate(words):
        if not isinstance(item,dict) or not str(item.get("word","")).strip(): raise ValueError(f"Word {index+1} is empty.")
        try: start=float(item["start"]); end=float(item["end"])
        except (KeyError,TypeError,ValueError): raise ValueError(f"Word {index+1} has missing or invalid timestamps.")
        if not math.isfinite(start) or not math.isfinite(end) or start<0 or end<=start: raise ValueError(f"Word {index+1} has an invalid time range.")
        if start+0.001<previous_start: raise ValueError(f"Word {index+1} is out of chronological order.")
        previous_start=start
    coverage=len(words)/max(1,int(expected_count or len(words)))
    if coverage<min_coverage: raise ValueError(f"Alignment coverage {coverage:.1%} is below {min_coverage:.0%}.")
    return coverage
