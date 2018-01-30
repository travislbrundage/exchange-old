#!/usr/bin/env python
# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2017 Boundless Spatial
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

import os
import sys
import unittest
import django

from requests import get, Session, Request, Response, ConnectionError
from requests.adapters import HTTPAdapter

from django.http import HttpRequest, HttpResponse
from django.conf import settings
from django.test.utils import get_runner
from django.test.runner import DiscoverRunner
from django.test import TestCase

from exchange.pki.settings import (SSL_DEFAULT_CONFIG,
                                   SSL_CONFIGS,
                                   SSL_CONFIG_MAP)
from exchange.pki.utils import (hostname_port,
                                requests_base_url,
                                SslContextAdapter,
                                get_ssl_context_opts)


TESTDIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'files')


# This represents an ssl_config model
SSL_CONFIGS.update({
    "config1": {
        "name": "Custom CAs",
        "ca_custom_certs": os.path.join(
            TESTDIR, 'subissuer-issuer-root-ca_issuer-2-root-2-ca_chains.pem'),
    },
    "config2": {
        "name": "PKI: key with no password",
        "ca_custom_certs": os.path.join(
            TESTDIR, 'subissuer-issuer-root-ca_issuer-2-root-2-ca_chains.pem'),
        "client_cert": os.path.join(TESTDIR, 'alice-cert.pem'),
        "client_key": os.path.join(TESTDIR, 'alice-key.pem'),
    },
    "config3": {
        "name": "PKI: key with password",
        "ca_custom_certs": os.path.join(
            TESTDIR, 'subissuer-issuer-root-ca_issuer-2-root-2-ca_chains.pem'),
        "client_cert": os.path.join(TESTDIR, 'alice-cert.pem'),
        "client_key": os.path.join(TESTDIR, 'alice-key_w-pass.pem'),
        "client_key_pass": "password",
    },
    "config4": {
        "name": "PKI: alt client root CA chain",
        "ca_custom_certs": os.path.join(
            TESTDIR, 'subissuer-issuer-root-ca_issuer-2-root-2-ca_chains.pem'),
        "client_cert": os.path.join(TESTDIR, 'jane-cert.pem'),
        "client_key": os.path.join(TESTDIR, 'jane-key_w-pass.pem'),
        "client_key_pass": "password",
    },
    "config5": {
        "name": "PKI: key with password; TLSv1_2-only",
        "ca_custom_certs": os.path.join(
            TESTDIR, 'subissuer-issuer-root-ca_issuer-2-root-2-ca_chains.pem'),
        "client_cert": os.path.join(TESTDIR, 'alice-cert.pem'),
        "client_key": os.path.join(TESTDIR, 'alice-key_w-pass.pem'),
        "client_key_pass": "password",
        "ssl_version": "PROTOCOL_TLSv1_2",
    },
    "config6": {
        "name": "PKI: key with no password; custom CAs with no validation",
        "ca_custom_certs": os.path.join(
            TESTDIR, 'subissuer-issuer-root-ca_issuer-2-root-2-ca_chains.pem'),
        "client_cert": os.path.join(TESTDIR, 'alice-cert.pem'),
        "client_key": os.path.join(TESTDIR, 'alice-key.pem'),
        "ssl_verify_mode": "CERT_NONE",
    },
    "config7": {
        "name": "PKI: key with no password; TLSv1_2-only (via ssl_options)",
        "ca_custom_certs": os.path.join(
            TESTDIR, 'subissuer-issuer-root-ca_issuer-2-root-2-ca_chains.pem'),
        "client_cert": os.path.join(TESTDIR, 'alice-cert.pem'),
        "client_key": os.path.join(TESTDIR, 'alice-key.pem'),
        "ssl_version": "PROTOCOL_SSLv23",
        "ssl_options": ['OP_NO_SSLv2', 'OP_NO_SSLv3', 'OP_NO_TLSv1',
                        'OP_NO_TLSv1_1', 'OP_NO_COMPRESSION'],
    },
    # "config": {
    #     "name": "PKI: use system CAs",
    #     "client_cert": os.path.join(TESTDIR, 'alice-cert.pem'),
    #     "client_key": os.path.join(TESTDIR, 'alice-key.pem'),
    # },
})


# This represents the pki app's view
def pki_request(resource_url=None):
    """
    :param resource_url:
    :rtype: HttpResponse
    """

    # skip Django request passing for now
    # skip Django path manipulation for now (just pass full URL for this test)

    # needed if SslContextAdapter internal normalization causes issues
    # url = normalize_hostname(resource_url)
    url = resource_url
    base_url = requests_base_url(resource_url)

    req_ses = Session()  # type: requests.Session

    # IMPORTANT: base_url is (scheme://hostname:port), not full url.
    # Note: urllib3 (as of 1.22) seems to care about case when matching the
    # hostname to the peer server's SSL cert, in contrast to the spec, which
    # says such matches should be case-insensitive (this is a bug):
    #   https://tools.ietf.org/html/rfc5280#section-4.2.1.6
    #   https://tools.ietf.org/html/rfc6125 <-- best practices
    req_ses.mount(base_url, SslContextAdapter(*get_ssl_context_opts(base_url)))
    # TODO: Passthru Django request headers, cookies, etc.
    # Should we be sending cookies from Exchange's domain into remote endpoint?
    req_res = req_ses.get(url)
    """:type: requests.Response"""
    # TODO: Capture errors and signal to Exchange UI for reporting to user.
    #       Don't let errors just raise exceptions

    # TODO: Passthru requests headers, cookies, etc.
    # Should we be setting cookies in Exchange's domain from remote endpoint?
    # TODO: Should we be sniffing encoding/charset and passing back?
    response = HttpResponse(
        content=req_res.content,
        status=req_res.status_code,
        reason=req_res.reason,
        content_type=req_res.headers.get('Content-Type'),
    )

    return response


# noinspection PyPep8Naming
def skipUnlessHasMapproxy():
    try:
        mp_http = get('http://mapproxy.boundless.test:8088')
        assert mp_http.status_code == 200
        return lambda func: func
    except (ConnectionError, AssertionError):
        return unittest.skip(
            'Test requires mapproxy docker-compose container running')


@skipUnlessHasMapproxy()
class TestPkiRequest(TestCase):

    @classmethod
    def setUpClass(cls):
        # This needs to be mixed case, to ensure SslContextAdapter handles
        # server cert matching always via lowercase hostname (bug in urllib3)
        cls.mp_root = 'https://maPproxy.Boundless.test:8344/'

        # Already know what the lookup table key should be like
        cls.mp_host_port = hostname_port(cls.mp_root)
        cls.mp_base = requests_base_url(cls.mp_root)

        cls.mp_txt = 'Welcome to MapProxy'

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_no_client(self):
        SSL_CONFIG_MAP[self.mp_host_port] = 'config1'
        res = pki_request(resource_url=self.mp_root)
        # Nginx non-standard status code 400 is for no client cert supplied
        self.assertEqual(res.status_code, 400)

    def test_client_no_password(self):
        SSL_CONFIG_MAP[self.mp_host_port] = 'config2'
        res = pki_request(resource_url=self.mp_root)
        self.assertEqual(res.status_code, 200)
        self.assertIn(self.mp_txt, res.content.decode("utf-8"))

    def test_client_and_password(self):
        SSL_CONFIG_MAP[self.mp_host_port] = 'config3'
        res = pki_request(resource_url=self.mp_root)
        self.assertEqual(res.status_code, 200)
        self.assertIn(self.mp_txt, res.content.decode("utf-8"))

    def test_client_and_password_alt_root(self):
        SSL_CONFIG_MAP[self.mp_host_port] = 'config4'
        res = pki_request(resource_url=self.mp_root)
        self.assertEqual(res.status_code, 200)
        self.assertIn(self.mp_txt, res.content.decode("utf-8"))

    def test_client_and_password_tls12_only(self):
        SSL_CONFIG_MAP[self.mp_host_port] = 'config5'
        res = pki_request(resource_url=self.mp_root)
        self.assertEqual(res.status_code, 200)
        self.assertIn(self.mp_txt, res.content.decode("utf-8"))

    def test_no_client_no_validation(self):
        SSL_CONFIG_MAP[self.mp_host_port] = 'config6'
        res = pki_request(resource_url=self.mp_root)
        self.assertEqual(res.status_code, 200)

    def test_client_no_password_tls12_only_ssl_opts(self):
        SSL_CONFIG_MAP[self.mp_host_port] = 'config7'
        res = pki_request(resource_url=self.mp_root)
        self.assertEqual(res.status_code, 200)


# def suite():
#     test_suite = unittest.makeSuite(TestPkiRequest, 'test')
#     return test_suite
#
#
# def run_all():
#     unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(suite())


if __name__ == '__main__':
    # unittest.main()

    # Use standard Django test runner to test reusable applications
    # https://docs.djangoproject.com/en/2.0/topics/testing/advanced/
    #         #using-the-django-test-runner-to-test-reusable-applications
    os.environ['DJANGO_SETTINGS_MODULE'] = 'test_settings'
    django.setup()
    TestRunner = get_runner(settings)
    """:type: django.test.runner.DiscoverRunner"""
    test_runner = TestRunner(keepdb=True)
    failures = test_runner.run_tests(['.'])
    sys.exit(bool(failures))
