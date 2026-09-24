"""Tests for certbot_dns_namecheap._internal.dns_namecheap."""
import sys
from unittest import mock

import pytest
from requests import Response
from requests.exceptions import HTTPError

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


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv[1:] + [__file__]))  # pragma: no cover
