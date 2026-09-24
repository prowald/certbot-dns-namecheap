"""Tests for certbot_dns_namecheap._internal.dns_namecheap."""
import sys
from unittest import mock

import pytest
from requests import Response
from requests.exceptions import HTTPError
from requests.exceptions import RequestException

from certbot import errors
from certbot.compat import os
from certbot.plugins import dns_test_common
from certbot.plugins import dns_test_common_lexicon
from certbot.tests import util as test_util

USERNAME = 'foo'
TOKEN = 'bar'
CLIENT_IP = '203.0.113.1'


class AuthenticatorTest(test_util.TempDirTestCase,
                        dns_test_common_lexicon.BaseLexiconDNSAuthenticatorTest):

    LOGIN_ERROR = HTTPError("401 Client Error: Unauthorized for url: ...", response=Response())

    def setUp(self):
        super().setUp()

        from certbot_dns_namecheap._internal.dns_namecheap import Authenticator

        path = os.path.join(self.tempdir, 'file.ini')
        dns_test_common.write({"namecheap_username": USERNAME,
                               "namecheap_token": TOKEN,
                               "namecheap_client_ip": CLIENT_IP}, path)

        self.config = mock.MagicMock(namecheap_credentials=path,
                                     namecheap_propagation_seconds=0)  # don't wait during tests

        self.auth = Authenticator(self.config, "namecheap")

    def _write_credentials(self, credentials):
        path = os.path.join(self.tempdir, 'other.ini')
        dns_test_common.write(credentials, path)
        self.config.namecheap_credentials = path
        self.auth._setup_credentials()  # pylint: disable=protected-access

    def _provider_option(self, name):
        config = self.auth._build_lexicon_config('example.com')  # pylint: disable=protected-access
        return config.resolve(f'lexicon:namecheap:{name}')

    def test_client_ip_from_credentials(self):
        self._write_credentials({"namecheap_username": USERNAME, "namecheap_token": TOKEN,
                                 "namecheap_client_ip": CLIENT_IP})
        with mock.patch('requests.get') as mock_get:
            self.assertEqual(CLIENT_IP, self._provider_option('auth_client_ip'))
        mock_get.assert_not_called()

    def test_client_ip_detected_when_missing(self):
        self._write_credentials({"namecheap_username": USERNAME, "namecheap_token": TOKEN})
        with mock.patch('requests.get') as mock_get:
            mock_get.return_value.text = '198.51.100.7\n'
            self.assertEqual('198.51.100.7', self._provider_option('auth_client_ip'))
            self.assertEqual('198.51.100.7', self._provider_option('auth_client_ip'))
        mock_get.assert_called_once()

    def test_client_ip_detection_failure(self):
        self._write_credentials({"namecheap_username": USERNAME, "namecheap_token": TOKEN})
        with mock.patch('requests.get', side_effect=RequestException('offline')):
            with self.assertRaises(errors.PluginError):
                self._provider_option('auth_client_ip')

    def test_legacy_api_key(self):
        self._write_credentials({"namecheap_username": USERNAME, "namecheap_api_key": TOKEN,
                                 "namecheap_client_ip": CLIENT_IP})
        self.assertEqual(TOKEN, self._provider_option('auth_token'))

    def test_missing_token(self):
        with self.assertRaises(errors.PluginError):
            self._write_credentials({"namecheap_username": USERNAME})


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv[1:] + [__file__]))  # pragma: no cover
