"""Tests for certbot_dns_namecheap.dns_namecheap."""

import os
import unittest

import mock
from requests.exceptions import HTTPError

from certbot.plugins import dns_test_common
from certbot.plugins import dns_test_common_lexicon
from certbot.tests import util as test_util

USERNAME = 'foo'
API_KEY = 'bar'


class AuthenticatorTest(test_util.TempDirTestCase,
                        dns_test_common_lexicon.BaseLexiconAuthenticatorTest):

    def setUp(self):
        super(AuthenticatorTest, self).setUp()

        from certbot_dns_namecheap._internal.dns_namecheap import Authenticator

        path = os.path.join(self.tempdir, 'file.ini')
        credentials = {
            "namecheap_username": USERNAME,
            "namecheap_api_key": API_KEY
        }
        dns_test_common.write(credentials, path)

        self.config = mock.MagicMock(namecheap_credentials=path,
                                     namecheap_propagation_seconds=0)  # don't wait during tests

        self.auth = Authenticator(self.config, "namecheap")

        self.mock_client = mock.MagicMock()
        # _get_namecheap_client | pylint: disable=protected-access
        self.auth._get_namecheap_client = mock.MagicMock(return_value=self.mock_client)


class NamecheapLexiconClientTest(unittest.TestCase, dns_test_common_lexicon.BaseLexiconClientTest):
    DOMAIN_NOT_FOUND = Exception('Domain example.com not found')
    LOGIN_ERROR = HTTPError('403 Client Error: Forbidden')

    def setUp(self):
        from certbot_dns_namecheap._internal.dns_namecheap import _NamecheapLexiconClient

        self.client = _NamecheapLexiconClient(
            USERNAME, API_KEY, 0, 'example.com'
        )

        self.provider_mock = mock.MagicMock()
        self.client.provider = self.provider_mock


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
