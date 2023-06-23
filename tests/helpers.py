from unittest import mock


def sealed_mock(**kwargs: object) -> mock.MagicMock:
    magic_mock = mock.MagicMock(**kwargs)
    mock.seal(magic_mock)
    return magic_mock
