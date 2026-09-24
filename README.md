# certbot-dns-namecheap

Namecheap DNS Authenticator plugin for [Certbot](https://certbot.eff.org/).

This plugin automates the process of completing a `dns-01` challenge by creating, and subsequently removing, TXT records using the [Namecheap API](https://www.namecheap.com/support/api/intro/). Internally it uses the Namecheap provider of [Lexicon](https://github.com/dns-lexicon/dns-lexicon).

Because it uses the `dns-01` challenge, the plugin can also issue wildcard certificates (e.g. `*.example.com`).

## Requirements

- Python 3.8 or newer
- Certbot 2.7.0 or newer
- A domain whose DNS is hosted by Namecheap (BasicDNS/PremiumDNS)

### Getting API access

Namecheap has certain requirements for activation to prevent system abuse. In order to have API access enabled for your account, you should meet at least one of the following requirements:

- have at least 20 domains under your account;
- have at least $50 on your account balance;
- have at least $50 spent within the last 2 years.

Enable API access and whitelist the public IPv4 address of the machine running Certbot on the [API Access page](https://ap.www.namecheap.com/settings/tools/apiaccess/) of your Namecheap account. Requests from IP addresses that are not whitelisted are rejected by Namecheap.

## Credentials

Use of this plugin requires a configuration file containing your Namecheap API credentials. All three values are required:

```ini
# Namecheap API credentials used by Certbot
dns_namecheap_username = my-username
dns_namecheap_token = my-api-key
dns_namecheap_client_ip = 203.0.113.1
```

| Key                       | Description                                              |
| ------------------------- | -------------------------------------------------------- |
| `dns_namecheap_username`  | Username of your Namecheap account                       |
| `dns_namecheap_token`     | API key from the API Access page                         |
| `dns_namecheap_client_ip` | Public IPv4 address whitelisted on the API Access page   |

The path to this file is provided with the `--dns-namecheap-credentials` command-line argument.

Protect the file like the password of your Namecheap account – anyone who can read it can use the API on your behalf. Certbot warns about unsafe permissions, so restrict access:

```sh
mkdir -p ~/.secrets/certbot
chmod 700 ~/.secrets/certbot
chmod 600 ~/.secrets/certbot/namecheap.ini
```

## Installation

### Python

Install the plugin into the same Python environment as `certbot`. If you are not sure how to do this, use the [Docker](#docker) approach below.

```sh
git clone https://github.com/prowald/certbot-dns-namecheap.git
pip install ./certbot-dns-namecheap
```

Check that `certbot` discovers the plugin – `dns-namecheap` should be listed:

```sh
certbot plugins
```

### Docker

The included `Dockerfile` builds on the official `certbot/certbot` image and installs the plugin:

```sh
git clone https://github.com/prowald/certbot-dns-namecheap.git
docker build -t certbot-dns-namecheap ./certbot-dns-namecheap
```

Run it with the Certbot directories and the credentials file mounted:

```sh
docker run --rm -it \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -v /var/lib/letsencrypt:/var/lib/letsencrypt \
  -v ~/.secrets/certbot/namecheap.ini:/namecheap.ini:ro \
  certbot-dns-namecheap certonly \
  --authenticator dns-namecheap \
  --dns-namecheap-credentials /namecheap.ini \
  -d example.com
```

## Usage

```sh
certbot certonly \
  --authenticator dns-namecheap \
  --dns-namecheap-credentials ~/.secrets/certbot/namecheap.ini \
  --agree-tos \
  --email "your@mail.com" \
  -d example.com \
  -d '*.example.com' \
  --test-cert
```

After a successful run, remove the `--test-cert` parameter (which uses the Let's Encrypt [staging environment](https://letsencrypt.org/docs/staging-environment/)) and run the command again to get a trusted certificate.

### Options

| Option                                  | Description                                                                                  |
| --------------------------------------- | -------------------------------------------------------------------------------------------- |
| `--dns-namecheap-credentials`           | Path to the Namecheap credentials INI file (required)                                         |
| `--dns-namecheap-propagation-seconds`   | Seconds to wait for DNS propagation before the ACME server verifies the record (default: 120) |

Namecheap DNS changes can take a while to propagate. If validation fails, increase the waiting time, e.g. `--dns-namecheap-propagation-seconds 300`.

## Development

```sh
pip install -e . pytest
pytest
```

## License

Apache License 2.0 – see [LICENSE.txt](LICENSE.txt).
