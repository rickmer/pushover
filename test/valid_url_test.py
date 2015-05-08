from pushover import _valid_url_


def test_url_invalid():
    assert not _valid_url_('gopher://test')


def test_url_http():
    assert _valid_url_('http://127.0.0.1:8080')


def test_url_https():
    assert _valid_url_('https://thisisatestdomain.test/1245')
