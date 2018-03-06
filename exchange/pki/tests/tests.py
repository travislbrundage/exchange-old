#!/usr/bin/env python
# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2018 Boundless Spatial
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
import logging
import django

from requests import get
from requests.exceptions import ConnectionError

# from django.http import HttpRequest, HttpResponse
from django.conf import settings
from django.test.utils import get_runner
from django.test import TestCase

TESTDIR = os.path.dirname(os.path.realpath(__file__))

if __name__ != '__main__':
    from ..models import (
        SslConfig,
        HostnamePortSslConfig,
        hostnameport_pattern_cache,
        ssl_config_for_url,
        has_ssl_config,
        hostnameport_pattern_for_url
    )
    from ..utils import hostname_port, requests_base_url
    from ..crypto import Crypto
    from ..ssl_adapter import (
        https_client,
        https_request,
        clear_https_adapters,
        ssl_config_to_context_opts,
        get_ssl_context_opts,
        SslContextAdapter
    )

logger = logging.getLogger(__name__)


def skip_unless_has_mapproxy():
    try:
        mp_http = get('http://mapproxy.boundless.test:8088')
        assert mp_http.status_code == 200
        return lambda func: func
    except (ConnectionError, AssertionError):
        return unittest.skip(
            'Test requires mapproxy docker-compose container running')


class TestHostnamePortSslConfig(TestCase):

    @classmethod
    def setUpClass(cls):
        # This needs to be mixed case, to ensure SslContextAdapter handles
        # server cert matching always via lowercase hostname (bug in urllib3)
        cls.mp_root = u'https://maPproxy.Boundless.test:8344/'

        # Already know what the lookup table key should be like
        cls.mp_host_port = hostname_port(cls.mp_root)

        cls.mp_txt = 'Welcome to MapProxy'

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        testheader = '\n\n#####_____ {0} _____#####' \
            .format(str(self).replace('pki.tests.tests.', ''))
        logger.debug(testheader)
        pass

    def tearDown(self):
        pass

    def testHostnamePortSslConfigSignals(self):
        clear_https_adapters()
        HostnamePortSslConfig.objects.all().delete()

        self.assertEqual(HostnamePortSslConfig.objects.count(), 0)
        self.assertEqual(len(https_client.adapters), 1)  # for http://

        ssl_config_1 = SslConfig.objects.get(pk=1)
        ssl_config_2 = SslConfig.objects.get(pk=2)
        ssl_config_3 = SslConfig.objects.get(pk=3)
        ssl_configs = [ssl_config_1, ssl_config_2, ssl_config_3]

        p1 = u'*.arcgisonline.com*'
        p2 = u'*.boundless.test*'
        p3 = u'*.*'
        ptrns = [p1, p2, p3]

        HostnamePortSslConfig.objects.create_hostnameportsslconfig(
            p1, ssl_config_1)
        self.assertEqual(hostnameport_pattern_cache, [p1])
        hnp_sslconfig_1 = HostnamePortSslConfig.objects.get(hostname_port=p1)
        HostnamePortSslConfig.objects.create_hostnameportsslconfig(
            p2, ssl_config_2)
        self.assertEqual(hostnameport_pattern_cache, [p1, p2])
        hnp_sslconfig_2 = HostnamePortSslConfig.objects.get(hostname_port=p2)
        HostnamePortSslConfig.objects.create_hostnameportsslconfig(
            p3, ssl_config_3)
        self.assertEqual(hostnameport_pattern_cache, [p1, p2, p3])
        hnp_sslconfig_3 = HostnamePortSslConfig.objects.get(hostname_port=p3)
        hnp_sslconfigs = [hnp_sslconfig_1, hnp_sslconfig_2, hnp_sslconfig_3]
        self.assertTrue(all(hnp_sslconfigs))

        url1 = u'https://services.arcgisonline.com/arcgis/rest/' \
               u'services/topic/layer/?f=pjson'
        url2 = u'https://maPproxy.Boundless.test:8344/service?' \
               u'service=WMS&request=GetCapabilities&version=1.1.1'
        url3 = u'https://привет.你好.çéàè.example.com/some/path?key=value#frag'
        urls = [url1, url2, url3]

        for p, config, url in zip(ptrns, ssl_configs, urls):
            self.assertTrue(has_ssl_config(url))
            ssl_config = ssl_config_for_url(url)
            self.assertIsNotNone(ssl_config)
            self.assertEqual(ssl_config, config)
            self.assertEqual(
                ssl_config_to_context_opts(ssl_config),
                ssl_config_to_context_opts(config)
            )
            self.assertEqual(hostnameport_pattern_for_url(url), p)

        for url, ssl_config in zip(urls, ssl_configs):
            base_url = requests_base_url(url)
            https_client.mount(
                base_url,
                SslContextAdapter(*get_ssl_context_opts(base_url))
            )
            adptr = https_client.adapters[base_url]
            """:type: SslContextAdapter"""
            self.assertEqual(adptr.context_options(),
                             ssl_config_to_context_opts(ssl_config))

        # return
        #
        # self.assertEqual(HostnamePortSslConfig.objects.count(), 1)
        # self.assertEqual(len(https_client.adapters), 2)
        #
        # adptr_1 = https_client.adapters[requests_base_url(self.mp_root)]
        # """:type: SslContextAdapter"""
        #
        # self.assertIsInstance(adptr_1, SslContextAdapter)
        #
        # self.assertEqual(ssl_config_to_context_opts(
        #     ssl_config_1), adptr_1.context_options())
        #
        # # Update ssl_config
        #
        # HostnamePortSslConfig.objects.create_hostnameportsslconfig(
        #     self.mp_root, ssl_config_2)
        #
        # self.assertEqual(HostnamePortSslConfig.objects.count(), 1)
        # self.assertEqual(len(https_client.adapters), 2)
        #
        # adptr_2 = https_client.adapters[requests_base_url(self.mp_root)]
        # """:type: SslContextAdapter"""
        #
        # self.assertIsInstance(adptr_2, SslContextAdapter)
        #
        # self.assertEqual(ssl_config_to_context_opts(
        #     ssl_config_2), adptr_2.context_options())
        #
        # # Delete first, unreferenced config
        # SslConfig.objects.get(pk=1).delete()
        # # nothing should have changed
        # self.assertEqual(HostnamePortSslConfig.objects.count(), 1)
        # self.assertEqual(len(https_client.adapters), 2)
        #
        # # Delete second, referenced config
        # SslConfig.objects.get(pk=2).delete()
        # # Should automatically remove mapping (related record) and
        # # adapter (via signal)
        # self.assertEqual(HostnamePortSslConfig.objects.count(), 0)
        # self.assertEqual(len(https_client.adapters), 1)


@skip_unless_has_mapproxy()
class TestPkiRequest(TestCase):

    @classmethod
    def setUpClass(cls):
        # This needs to be mixed case, to ensure SslContextAdapter handles
        # server cert matching always via lowercase hostname (bug in urllib3)
        cls.mp_root = u'https://maPproxy.Boundless.test:8344/'

        # Already know what the lookup table key should be like
        cls.mp_host_port = hostname_port(cls.mp_root)

        cls.mp_txt = 'Welcome to MapProxy'

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        # HostnamePortSslConfig.objects.all().delete()
        testheader = '\n\n#####_____ {0} _____#####'\
            .format(str(self).replace('pki.tests.tests.', ''))
        logger.debug(testheader)
        pass

    def tearDown(self):
        # HostnamePortSslConfig.objects.all().delete()
        pass

    def _set_hostname_port_mapping(self, pk, ptn=None):
        if ptn is None:
            ptn = self.mp_host_port
        logger.debug("Attempt Hostname:Port mapping for SslConfig pk: {0}"
                     .format(pk))
        ssl_config = SslConfig.objects.get(pk=pk)
        HostnamePortSslConfig.objects.create_hostnameportsslconfig(
            ptn, ssl_config)
        logger.debug("Hostname:Port mappings:\n{0}"
                     .format(HostnamePortSslConfig.objects.all()))

    def test_crypto(self):
        c = Crypto()
        data = 'abcd'
        self.assertEqual(c.decrypt(c.encrypt(data)), data)
        udata = u'abcd'
        self.assertEqual(c.decrypt(c.encrypt(udata)), data)
        udata = u'abcd'
        self.assertEqual(c.decrypt(c.encrypt(udata)), data)
        accdata = 'çéàè↓'
        self.assertEqual(c.decrypt(c.encrypt(accdata)), accdata)
        uaccdata = u'çéàè↓'
        self.assertEqual(c.decrypt(c.encrypt(uaccdata)), accdata)

    def test_default_config(self):
        config_1 = SslConfig.objects.get(pk=1)
        self.assertEqual(config_1, SslConfig.default_ssl_config())
        del config_1

        # Simulate admin removing it
        SslConfig.objects.get(pk=1).delete()
        with self.assertRaises(SslConfig.DoesNotExist):
            SslConfig.objects.get(pk=1)

        # Re-add default
        SslConfig.objects.create_default()
        config_1 = SslConfig.objects.get_create_default()
        self.assertEqual(config_1, SslConfig.default_ssl_config())

        config_1.https_retries = False
        config_1.save()
        host_port_map = HostnamePortSslConfig(
            hostname_port=self.mp_host_port,
            ssl_config=config_1)
        host_port_map.save()
        res = https_request(self.mp_root)
        self.assertIsNone(res)

        host_port_map = HostnamePortSslConfig(
            hostname_port='example.com',
            ssl_config=config_1)
        host_port_map.save()
        res = https_request('https://example.com')
        self.assertEqual(res.status_code, 200)

    def test_no_client(self):
        self._set_hostname_port_mapping(2)
        res = https_request(self.mp_root)
        # Nginx non-standard status code 400 is for no client cert supplied
        self.assertEqual(res.status_code, 400)

    def test_client_no_password(self):
        self._set_hostname_port_mapping(3)
        res = https_request(self.mp_root)
        self.assertEqual(res.status_code, 200)
        self.assertIn(self.mp_txt, res.content.decode("utf-8"))

    def test_client_and_password(self):
        self._set_hostname_port_mapping(4)
        res = https_request(self.mp_root)
        self.assertEqual(res.status_code, 200)
        self.assertIn(self.mp_txt, res.content.decode("utf-8"))

    def test_client_and_password_alt_root(self):
        self._set_hostname_port_mapping(5)
        res = https_request(self.mp_root)
        self.assertEqual(res.status_code, 200)
        self.assertIn(self.mp_txt, res.content.decode("utf-8"))

    def test_client_and_password_tls12_only(self):
        self._set_hostname_port_mapping(6)
        res = https_request(self.mp_root)
        self.assertEqual(res.status_code, 200)
        self.assertIn(self.mp_txt, res.content.decode("utf-8"))

    def test_no_client_no_validation(self):
        self._set_hostname_port_mapping(7)
        res = https_request(self.mp_root)
        self.assertEqual(res.status_code, 200)

    def test_client_no_password_tls12_only_ssl_opts(self):
        self._set_hostname_port_mapping(8)
        res = https_request(self.mp_root)
        self.assertEqual(res.status_code, 200)


if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.dirname(TESTDIR)))
    # print(sys.path)
    os.chdir(os.path.dirname(os.path.dirname(TESTDIR)))
    # print(os.getcwd())

    # Use standard Django test runner to test reusable applications
    # https://docs.djangoproject.com/en/2.0/topics/testing/advanced/
    #         #using-the-django-test-runner-to-test-reusable-applications
    os.environ['DJANGO_SETTINGS_MODULE'] = 'test_settings'
    django.setup()

    # These imports need to come after loading settings, since settings is
    # imported in crypto.Crypto class, for SECRET_KEY use
    from pki.models import SslConfig, HostnamePortSslConfig  # noqa
    from pki.utils import hostname_port, requests_base_url  # noqa
    from pki.crypto import Crypto  # noqa
    from pki.ssl_adapter import https_client  # noqa
    from pki.ssl_adapter import https_request  # noqa
    from pki.ssl_adapter import clear_https_adapters  # noqa
    from pki.ssl_adapter import ssl_config_to_context_opts  # noqa
    from pki.ssl_adapter import SslContextAdapter  # noqa

    TestRunner = get_runner(settings)
    """:type: django.test.runner.DiscoverRunner"""
    test_runner = TestRunner(keepdb=False)
    failures = test_runner.run_tests(['pki.tests'])
    sys.exit(bool(failures))
