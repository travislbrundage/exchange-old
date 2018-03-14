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

import unittest
import logging
# noinspection PyPackageRequirements
import pytest
import django

from requests import get
from requests.exceptions import ConnectionError

from django.core import management
from django.core.exceptions import ImproperlyConfigured, AppRegistryNotReady

try:
    # Do this before geonode.services.serviceprocessors, so that apps are ready
    django.setup()
except (RuntimeError, ImproperlyConfigured,
        AppRegistryNotReady, LookupError, ValueError):
    raise

from geonode.services import enumerations
from geonode.services.serviceprocessors import get_service_handler

from . import ExchangeTest

from exchange.pki.models import (
    SslConfig,
    HostnamePortSslConfig,
    hostnameport_pattern_cache,
    ssl_config_for_url,
    has_ssl_config,
    hostnameport_pattern_for_url,
)
from exchange.pki.utils import (
    hostname_port,
    requests_base_url,
    get_pki_dir,
)
from exchange.pki.crypto import Crypto
from exchange.pki.ssl_adapter import (
    https_client,
    https_request,
    clear_https_adapters,
    ssl_config_to_context_opts,
    get_ssl_context_opts,
    SslContextAdapter,
)

logger = logging.getLogger(__name__)


# bury these warnings for testing
class RemovedInDjango19Warning(Exception):
    pass


def skip_unless_has_mapproxy():
    try:
        mp_http = get('http://mapproxy.boundless.test:8088')
        assert mp_http.status_code == 200
        return lambda func: func
    except (ConnectionError, AssertionError):
        return unittest.skip(
            'Test requires mapproxy docker-compose container running')


def has_mapproxy():
    try:
        mp_http = get('http://mapproxy.boundless.test:8088')
        assert mp_http.status_code == 200
        return True
    except (ConnectionError, AssertionError):
        return False


class PkiTestCase(ExchangeTest):

    # fixtures = ['test_ssl_configs.json']
    fixtures = ['test_ssl_configs_no_default.json']

    @classmethod
    def setUpClass(cls):
        # django.setup()
        management.call_command('rebuild_index')
        super(PkiTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(PkiTestCase, cls).tearDownClass()

    @classmethod
    def setUpTestData(cls):
        """Load initial data for the TestCase"""
        # This needs to be mixed case, to ensure SslContextAdapter handles
        # server cert matching always via lowercase hostname (bug in urllib3)
        cls.mp_root = u'https://maPproxy.Boundless.test:8344/'

        # Already know what the lookup table key should be like
        cls.mp_host_port = hostname_port(cls.mp_root)

        cls.mp_txt = 'Welcome to MapProxy'

        logger.debug("PKI_DIRECTORY: {0}".format(get_pki_dir()))

        logger.debug("SslConfig.objects:\n{0}"
                     .format(repr(SslConfig.objects.all())))

    def create_hostname_port_mapping(self, ssl_config, ptn=None):
        if ptn is None:
            ptn = self.mp_host_port
        logger.debug("Attempt Hostname:Port mapping for SslConfig: {0}"
                     .format(ssl_config))
        if isinstance(ssl_config, int):
            ssl_config = SslConfig.objects.get(pk=ssl_config)
        if not isinstance(ssl_config, SslConfig):
            raise Exception('ssl_config not an instance of SslConfig')
        HostnamePortSslConfig.objects.create_hostnameportsslconfig(
            ptn, ssl_config)
        logger.debug("Hostname:Port mappings:\n{0}"
                     .format(HostnamePortSslConfig.objects.all()))


class TestHostnamePortSslConfig(PkiTestCase):

    def setUp(self):
        HostnamePortSslConfig.objects.all().delete()
        self.assertEqual(HostnamePortSslConfig.objects.count(), 0)

        self.ssl_config_1 = SslConfig.objects.get(pk=1)
        self.ssl_config_2 = SslConfig.objects.get(pk=2)
        self.ssl_config_3 = SslConfig.objects.get(pk=3)
        self.ssl_config_4 = SslConfig.objects.get(pk=4)
        self.ssl_config_5 = SslConfig.objects.get(pk=5)
        self.ssl_config_6 = SslConfig.objects.get(pk=6)
        self.ssl_config_7 = SslConfig.objects.get(pk=7)
        self.ssl_config_8 = SslConfig.objects.get(pk=8)
        self.ssl_configs = [
            self.ssl_config_1,  # Default: TLS-only
            self.ssl_config_4,  # PKI: key with password
            self.ssl_config_2   # Just custom CAs
        ]

        self.p1 = u'*.arcgisonline.com*'
        self.p2 = u'*.boundless.test*'
        self.p3 = u'*.*'
        self.ptrns = [self.p1, self.p2, self.p3]

        ptrns_l = []
        self.hnp_sslconfigs = []
        for config, p in zip(self.ssl_configs, self.ptrns):
            self.create_hostname_port_mapping(config, p)
            ptrns_l.append(p)
            self.assertEqual(hostnameport_pattern_cache, ptrns_l)

            self.hnp_sslconfigs.append(HostnamePortSslConfig.objects.get(
                hostname_port=p))
        self.assertTrue(all(self.hnp_sslconfigs))

    def tearDown(self):
        pass

    def testHostnamePortSslConfigSignals(self):
        clear_https_adapters()
        self.assertEqual(len(https_client.adapters), 1)  # for http://

        url1 = u'https://services.arcgisonline.com/arcgis/rest/' \
               u'services/topic/layer/?f=pjson'
        url2 = u'https://maPproxy.Boundless.test:8344/service?' \
               u'service=WMS&request=GetCapabilities&version=1.1.1'
        url3 = u'https://привет.你好.çéàè.example.com/some/path?key=value#frag'
        urls = [url1, url2, url3]

        for p, config, url in zip(self.ptrns, self.ssl_configs, urls):
            self.assertTrue(has_ssl_config(url))
            ssl_config = ssl_config_for_url(url)
            self.assertIsNotNone(ssl_config)
            self.assertEqual(ssl_config, config)
            self.assertEqual(
                ssl_config_to_context_opts(ssl_config),
                ssl_config_to_context_opts(config)
            )
            self.assertEqual(hostnameport_pattern_for_url(url), p)

        for url, ssl_config in zip(urls, self.ssl_configs):
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

    @pytest.mark.skip(reason="Just cause")
    def testMapProxyRegistration(self):
        mp_service = self.mp_root + 'service'

        handler = get_service_handler(
            base_url=mp_service, service_type=enumerations.WMS)
        result = handler.create_geonode_service(self.test_user)
        self.assertEqual(result.base_url, mp_service.lower())
        self.assertEqual(result.type, handler.service_type)
        self.assertEqual(result.method, handler.indexing_method)
        self.assertEqual(result.owner, self.test_user)
        self.assertEqual(result.name, handler.name)


@pytest.mark.skipif(
    not has_mapproxy(),
    reason='Test requires mapproxy docker-compose container running')
class TestPkiRequest(PkiTestCase):

    def setUp(self):
        HostnamePortSslConfig.objects.all().delete()

    def tearDown(self):
        HostnamePortSslConfig.objects.all().delete()

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
        self.create_hostname_port_mapping(2)
        res = https_request(self.mp_root)
        # Nginx non-standard status code 400 is for no client cert supplied
        self.assertEqual(res.status_code, 400)

    def test_client_no_password(self):
        self.create_hostname_port_mapping(3)
        res = https_request(self.mp_root)
        self.assertEqual(res.status_code, 200)
        self.assertIn(self.mp_txt, res.content.decode("utf-8"))

    def test_client_and_password(self):
        self.create_hostname_port_mapping(4)
        res = https_request(self.mp_root)
        self.assertEqual(res.status_code, 200)
        self.assertIn(self.mp_txt, res.content.decode("utf-8"))

    def test_client_and_password_alt_root(self):
        self.create_hostname_port_mapping(5)
        res = https_request(self.mp_root)
        self.assertEqual(res.status_code, 200)
        self.assertIn(self.mp_txt, res.content.decode("utf-8"))

    def test_client_and_password_tls12_only(self):
        self.create_hostname_port_mapping(6)
        res = https_request(self.mp_root)
        self.assertEqual(res.status_code, 200)
        self.assertIn(self.mp_txt, res.content.decode("utf-8"))

    def test_no_client_no_validation(self):
        self.create_hostname_port_mapping(7)
        res = https_request(self.mp_root)
        self.assertEqual(res.status_code, 200)

    def test_client_no_password_tls12_only_ssl_opts(self):
        self.create_hostname_port_mapping(8)
        res = https_request(self.mp_root)
        self.assertEqual(res.status_code, 200)
