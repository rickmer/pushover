from pushover import _valid_auth_


def test_auth_invalid():
    assert not _valid_auth_('asdfasdfdsaklgjfdsljfdslkghjlfdkjsghlskdfjhglksdfjghlksdfjhglsdfkhjksdfjhgfdsjklghlkjdfshglksdfghjlksdfjhglkjsdfhglkjdfshglkjhdsflkglksdjfgh')


def test_auth_valid():
    assert _valid_auth_('user123:pass123')
