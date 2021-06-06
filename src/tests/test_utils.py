import pytest
from utils import extract_from_regex, SMS_REGEX

def test_regex_extraction():
    text = "Your OTP to register/access CoWIN is 459831. It will be valid for 3 minutes. - CoWIN"
    output = extract_from_regex(text, SMS_REGEX)
    assert output == "459831"

    text = "This text has no valid OTP 34"
    output = extract_from_regex(text, SMS_REGEX)
    assert output is None
