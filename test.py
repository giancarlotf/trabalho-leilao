import web_scraping as ws

def test_validate_url():
    assert ws.validate_url("https://google.com") is None
    assert ws.validate_url("abc") is not None

def test_read_last_value():
    history = ["2024-01-01 | 10\n"]
    assert ws.read_last_value(history) == "10"