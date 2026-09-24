"""DNS Authenticator for Namecheap DNS."""
import logging
from typing import Any
from typing import Callable
from typing import Optional

import requests
from lexicon.config import ConfigResolver
from requests import HTTPError

from certbot import errors
from certbot.plugins import dns_common
from certbot.plugins import dns_common_lexicon

logger = logging.getLogger(__name__)

API_URL = "https://ap.www.namecheap.com/settings/tools/apiaccess/"
# Namecheap only accepts IPv4 addresses as ClientIP
PUBLIC_IP_URL = "https://api.ipify.org"


class Authenticator(dns_common_lexicon.LexiconDNSAuthenticator):
    """DNS Authenticator for Namecheap

    This Authenticator uses the Namecheap API to fulfill a dns-01 challenge.
    """

    description = 'Obtain certificates using a DNS TXT record (if you are using Namecheap for DNS).'

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._client_ip: Optional[str] = None

    @classmethod
    def add_parser_arguments(cls, add: Callable[..., None],
                             default_propagation_seconds: int = 120) -> None:
        super(Authenticator, cls).add_parser_arguments(add, default_propagation_seconds)
        add('credentials', help='Namecheap credentials INI file.')

    def more_info(self):
        return 'This plugin configures a DNS TXT record to respond to a dns-01 challenge using ' + \
               'the Namecheap API.'

    @property
    def _provider_name(self) -> str:
        return 'namecheap'

    def _setup_credentials(self) -> None:
        self._credentials = self._configure_credentials(
            key='credentials',
            label='Namecheap credentials INI file',
            required_variables={
                'username': 'username associated with Namecheap account',
            },
            validator=self._validate_credentials,
        )

    @staticmethod
    def _validate_credentials(credentials: dns_common.CredentialsConfiguration) -> None:
        # "api_key" is the name used by older versions of this plugin
        if not credentials.conf('token') and not credentials.conf('api_key'):
            raise errors.PluginError(
                f'Missing property in credentials configuration file {credentials.confobj.filename}:'
                f'\n * Property "{credentials.mapper("token")}" not found '
                f'(API token for Namecheap account, obtained from {API_URL}).')

    def _get_client_ip(self) -> str:
        if self._client_ip is None:
            self._client_ip = self._credentials.conf('client_ip')
        if not self._client_ip:
            try:
                response = requests.get(PUBLIC_IP_URL, timeout=30)
                response.raise_for_status()
            except requests.RequestException as e:
                raise errors.PluginError(
                    f'Unable to determine the public IP address via {PUBLIC_IP_URL}: {e}. '
                    f'Set "{self._credentials.mapper("client_ip")}" in the credentials file.')
            self._client_ip = response.text.strip()
            logger.debug('Using detected public IP address %s as Namecheap ClientIP',
                         self._client_ip)
        return self._client_ip

    def _build_lexicon_config(self, domain: str) -> ConfigResolver:
        if not hasattr(self, '_credentials'):  # pragma: no cover
            self._setup_credentials()

        dict_config = {
            'domain': domain,
            # Bypass Lexicon subdomain resolution, see LexiconDNSAuthenticator
            'delegated': domain,
            'provider_name': self._provider_name,
            'ttl': self._ttl,
            self._provider_name: {
                'auth_username': self._credentials.conf('username'),
                'auth_token': (self._credentials.conf('token')
                               or self._credentials.conf('api_key')),
                'auth_client_ip': self._get_client_ip(),
            },
        }
        return ConfigResolver().with_dict(dict_config).with_env()

    def _handle_http_error(self, e: HTTPError, domain_name: str) -> errors.PluginError:
        hint = None
        if str(e).startswith('401 Client Error: Unauthorized for url:'):
            hint = 'Are your username, API token and whitelisted client IP correct?'

        hint_disp = f' ({hint})' if hint else ''

        return errors.PluginError(f'Error determining zone identifier for {domain_name}: '
                                  f'{e}.{hint_disp}')
