"""DNS Authenticator for Namecheap DNS."""
import logging
from typing import Any
from typing import Callable

from requests import HTTPError

from certbot import errors
from certbot.plugins import dns_common_lexicon

logger = logging.getLogger(__name__)

API_URL = "https://ap.www.namecheap.com/settings/tools/apiaccess/"


class Authenticator(dns_common_lexicon.LexiconDNSAuthenticator):
    """DNS Authenticator for Namecheap

    This Authenticator uses the Namecheap API to fulfill a dns-01 challenge.
    """

    description = 'Obtain certificates using a DNS TXT record (if you are using Namecheap for DNS).'

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._add_provider_option('username',
                                  'username associated with Namecheap account',
                                  'auth_username')
        self._add_provider_option('token',
                                  f'API token for Namecheap account, obtained from {API_URL}',
                                  'auth_token')
        self._add_provider_option('client_ip', 
                                  'IP address whitelisted in Namecheap',
                                  'auth_client_ip')

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

    def _handle_http_error(self, e: HTTPError, domain_name: str) -> errors.PluginError:
        hint = None
        if str(e).startswith('401 Client Error: Unauthorized for url:'):
            hint = 'Are your email and API token values correct?'

        hint_disp = f' ({hint})' if hint else ''

        return errors.PluginError(f'Error determining zone identifier for {domain_name}: '
                                  f'{e}.{hint_disp}')
