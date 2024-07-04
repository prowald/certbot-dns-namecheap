"""
The `~certbot_dns_namecheap.dns_namecheap` plugin automates the process of
completing a ``dns-01`` challenge (`~acme.challenges.DNS01`) by creating, and
subsequently removing, TXT records using the Namecheap API.


Named Arguments
---------------

===================================  ==========================================
``--certbot-dns-namecheap:dns-namecheap-credentials`` Namecheap credentials_ INI file.
                                                      (Required)

===================================  ==========================================


Credentials
-----------

Use of this plugin requires a configuration file containing Namecheap
API credentials for an account with the following access rules:

.. code-block:: ini
   :name: credentials.ini
   :caption: Example credentials file:

	# Namecheap API credentials used by Certbot
	certbot_dns_namecheap:dns_namecheap_username=my-username
	certbot_dns_namecheap:dns_namecheap_api_key=my-api-key

The path to this file must be provided using the
``--certbot-dns-namecheap:dns-namecheap-credentials`` command-line argument.

.. caution::
   You should protect these API credentials as you would the password to your
   Namecheap account. Users who can read this file can use these credentials
   to issue arbitrary API calls on your behalf. Users who can cause Certbot to
   run using these credentials can complete a ``dns-01`` challenge to acquire
   new certificates or revoke existing certificates for associated domains,
   even if those domains aren't being managed by this server.

Certbot will emit a warning if it detects that the credentials file can be
accessed by other users on your system. The warning reads "Unsafe permissions
on credentials configuration file", followed by the path to the credentials
file. This warning will be emitted each time Certbot uses the credentials file,
including for renewal, and cannot be silenced except by addressing the issue
(e.g., by using a command like ``chmod 600`` to restrict access to the file).


Examples
--------

.. code-block:: bash
   :caption: To acquire a certificate for ``example.com``

   certbot certonly \\
     -a certbot-dns-namecheap:dns-namecheap \\
     --certbot-dns-namecheap:dns-namecheap-credentials= ~/.secrets/certbot/namecheap.ini \\
     -d example.com

.. code-block:: bash
   :caption: To acquire a single certificate for both ``example.com`` and
             ``www.example.com``

   certbot certonly \\
     -a certbot-dns-namecheap:dns-namecheap \\
     --certbot-dns-namecheap:dns-namecheap-credentials= ~/.secrets/certbot/namecheap.ini \\
     -d example.com
     -d www.example.com


"""
