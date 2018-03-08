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

import logging

from fnmatch import fnmatch

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import (
    rebuild_hostnameport_pattern_cache,
    HostnamePortSslConfig
)
from .ssl_adapter import (
    https_client,
    SslContextAdapter,
    get_ssl_context_opts,
    ssl_config_to_context_opts
)
from .utils import hostname_port

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
            continue  # only work with https
        if not isinstance(adpter, SslContextAdapter):
            continue  # just in case; this shouldn't happen
        ptn = None
        for p in ssl_configs.keys():
            if fnmatch(hostname_port(base_url), p):
                ptn = p
                break
        if ptn is not None:
            logger.debug(u'Adapter URL matched hostname:port pattern: '
                         u'{0} > {1}'.format(base_url, ptn))
            config = ssl_configs[ptn]
            if adpter.context_options() != ssl_config_to_context_opts(config):
                # SslConfig differs, replace
                adpter.close()  # clean up session pool manager
                # The mount() call wraps a dictionary[key] = value assignment,
                # so works for either creation or update.
                https_client.mount(
                    base_url,
                    SslContextAdapter(*get_ssl_context_opts(base_url))
                )
                logger.debug(u'Updated session adapter: {0}'.format(base_url))
            else:
                logger.debug(u'Session adapter unchanged: {0}'.format(base_url))
        else:
            logger.debug(u'Adapter URL does not match any hostname:port '
                         u'(deleting): {0}'.format(base_url))
            del https_client.adapters[base_url]


def sync_map_layers():
    """
    Sync/add saved map layer's flag that indicates it be requested through
    /pki route (via GeoNode's /proxy route) when changes occur to the
    HostnamePortSslConfig mappings, including reordering.

    Note: The flag can be added if the map layer's URL now maps to an
    SslConfig, even if it may not have mapped upon initial saving.
    """
    # TODO: Like, the actual code and everything
    pass


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
    sync_map_layers()
