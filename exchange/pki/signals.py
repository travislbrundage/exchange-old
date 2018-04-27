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

import json
import logging

from fnmatch import fnmatch

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from geonode.base.models import Link
from geonode.maps.models import MapLayer

from .models import (
    rebuild_hostnameport_pattern_cache,
    hostnameport_pattern_for_url,
    HostnamePortSslConfig
)
from .ssl_adapter import SslContextAdapter
from .ssl_session import https_client
from .utils import (
    hostname_port,
    has_proxy_prefix,
    proxy_route,
    proxy_route_reverse
)

logger = logging.getLogger(__name__)


def sync_https_adapters():
    """
    Sync any https_client session SslContextAdapters when changes occur to the
    HostnamePortSslConfig mappings, including reordering.

    Update any adapters that have newly mapped SslConfigs; remove any that no
    longer map to an SslConfig.

    Note: Can not ADD a session adapter here, as the adapter's key is based
    upon the base url of a connection's URL. This function merely performs
    housekeeping tasks on existing adapters.
    """
    adapters = https_client.adapters
    """:type: dict[str, SslContextAdapter]"""
    ssl_configs = HostnamePortSslConfig.objects.mapped_ssl_configs()
    """:type: dict[str, SslConfig]"""

    for base_url, adpter in adapters.items():
        if base_url.startswith('http://'):
            continue  # only work with https adapters
        ptn = None
        for p in ssl_configs.keys():
            if fnmatch(hostname_port(base_url), p):
                ptn = p
                break
        if ptn is not None:
            logger.debug(u'Adapter URL matched hostname:port pattern: '
                         u'{0} > {1}'.format(base_url, ptn))
            config = ssl_configs[ptn]
            if (not isinstance(adpter, SslContextAdapter) or
                    (adpter.context_options() !=
                     SslContextAdapter.ssl_config_to_context_opts(config))):
                # SslConfig differs, or needs to be SslContextAdapter; replace
                adpter.close()  # clean up session pool manager
                # The mount() call wraps a dictionary[key] = value assignment,
                # so works for either creation or update, but we want to be
                # sure there are no orphans.
                del https_client.adapters[base_url]
                https_client.mount_sslcontext_adapter(base_url)
                act = u'updated' \
                    if isinstance(adpter, SslContextAdapter) else u'added'
                logger.debug(u'Session SslContextAdapter {0}: {1}'
                             .format(act, base_url))
            else:
                logger.debug(u'Session SslContextAdapter unchanged: {0}'
                             .format(base_url))
            logging.debug(u'https_client Session.adapters: {0}'
                          .format(https_client.adapters))
        elif isinstance(adpter, SslContextAdapter):
            logger.debug(u'SslContextAdapter URL no longer matches any '
                         u'hostname:port pattern (deleting): {0}'
                         .format(base_url))
            adpter.close()  # clean up session pool manager
            del https_client.adapters[base_url]
        else:
            logger.debug(u'Session adapter is non-SslContextAdapter and does '
                         u'not match pattern (skipping): {0}'
                         .format(base_url))
            continue


def sync_layer_legend_urls():
    """
        Sync saved layer's legend URL that indicates it be requested through
        /pki route (via GeoNode's /proxy route) when changes occur to the
        HostnamePortSslConfig mappings, including reordering.

        Note: The update can happen if the map layer's URL now maps to an
        SslConfig, even if it may not have mapped upon initial saving.

        Important: Proxying is triggered if a mapping is enabled and matched,
        as the JS map viewers manage/generate the legend link themselves from
        the layer's base URL. This legend link is currently only shown on
        the layer/map details page.
        """
    links = list(Link.objects.filter(name='Legend').order_by('url'))
    """:type: list[geonode.base.models.Link]"""

    for link in links:
        if not link.url.lower().startswith('https') \
                and not has_proxy_prefix(link.url):
            # logger.debug(u'Skipping URL hostname:port pattern matching: '
            #              u'{0} > {1}'.format(link.link_type, link.url))
            continue

        orig_url = proxy_route_reverse(link.url)
        ptn = hostnameport_pattern_for_url(orig_url)
        if ptn is not None:
            logger.debug(u'Original link URL matched hostname:port pattern: '
                         u'{0} > {1}'.format(orig_url, ptn))
            # Legend graphic URLs should be proxied through geonode
            new_url = proxy_route(orig_url)
        else:
            logger.debug(u'Original link URL does not match any hostname:port:'
                         u' {0}'.format(orig_url))
            new_url = orig_url

        if new_url != link.url:
            link.url = new_url
            link.save(update_fields=['url'])


def sync_map_layers():
    """
    Sync/add saved map layer's flag that indicates it be requested through
    /pki route (via GeoNode's /proxy route) when changes occur to the
    HostnamePortSslConfig mappings, including reordering.

    Note: The flag can be added if the map layer's URL now maps to an
    SslConfig, even if it may not have mapped upon initial saving.
    """
    map_lyrs = list(MapLayer.objects.exclude(ows_url__isnull=True))
    """:type: list[geonode.maps.models.MapLayer]"""

    for map_lyr in map_lyrs:
        ptn = hostnameport_pattern_for_url(map_lyr.ows_url, uses_proxy=True)
        if ptn is not None:
            logger.debug(u'MapLayer URL matched hostname:port proxy pattern:'
                         u'{0} > {1}'.format(map_lyr, ptn))
        else:
            logger.debug(u'MapLayer URL does not match any proxied '
                         u'hostname:port: {0}'.format(map_lyr))
        src_params = json.loads(map_lyr.source_params)
        src_params['use_proxy'] = (ptn is not None)
        map_lyr.source_params = json.dumps(src_params)
        map_lyr.save(update_fields=['source_params'])


# noinspection PyUnusedLocal
@receiver(post_save, sender='pki.HostnamePortSslConfig',
          dispatch_uid='pki_signals_post_save')
def add_update_mapping(sender, instance, created, raw,
                       using, update_fields, **kwargs):
    """
    Respond to HostnamePortSslConfig adds/updates
    """
    rebuild_hostnameport_pattern_cache()
    sync_https_adapters()
    sync_layer_legend_urls()
    sync_map_layers()


# noinspection PyUnusedLocal
@receiver(post_delete, sender='pki.HostnamePortSslConfig',
          dispatch_uid='pki_signals_post_delete')
def remove_mapping(sender, instance, using, **kwargs):
    """
    Respond to HostnamePortSslConfig deletions
    """
    rebuild_hostnameport_pattern_cache()
    sync_https_adapters()
    sync_layer_legend_urls()
    sync_map_layers()
