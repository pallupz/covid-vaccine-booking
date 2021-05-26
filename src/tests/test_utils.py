import pytest
from utils import extract_from_regex

def test_regex_extraction():
    text = "Your OTP to register/access CoWIN is 459831. It will be valid for 3 minutes. - CoWIN"
    pattern = r"(?<!\d)\d{6}(?!\d)"
    output = extract_from_regex(text, pattern)
    assert "459831" == output

    text = "This text has no valid OTP 34"
    output = extract_from_regex(text, pattern)
    assert None == output