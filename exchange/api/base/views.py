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

from . import serializers
from geonode.layers.models import Layer
from geonode.base.models import TopicCategory
from rest_framework import viewsets
from rest_framework.response import Response
from exchange.views import get_exchange_version, \
    get_geoserver_version, get_pip_version
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from oauth2_provider.models import Application


class LayerViewSet(viewsets.ModelViewSet):
    queryset = Layer.objects.all()
    lookup_field = 'typename'
    serializer_class = serializers.LayerSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = TopicCategory.objects.all()
    serializer_class = serializers.CategorySerializer


class CapabilitiesViewSet(viewsets.ViewSet):

    """
    The capabilities view is like the about page, but
    for consumption by code instead of humans.
    It serves to provide information about the Exchange instance.
    """

    def list(self, request):

        exchange_version = get_exchange_version()

        geoserver_version = get_geoserver_version()
        geonode_version = get_pip_version('GeoNode')
        maploom_version = get_pip_version('django-exchange-maploom')
        importer_version = get_pip_version('django-osgeo-importer')
        react_version = get_pip_version('django-geonode-client')

        projects = [{
            'name': 'Boundless Exchange',
            'website': 'https://boundlessgeo.com/boundless-exchange/',
            'repo': 'https://github.com/boundlessgeo/exchange',
            'version': exchange_version['version'],
            'commit': exchange_version['commit']
        }, {
            'name': 'GeoNode',
            'website': 'http://geonode.org/',
            'repo': 'https://github.com/GeoNode/geonode',
            'boundless_repo': 'https://github.com/boundlessgeo/geonode',
            'version': geonode_version['version'],
            'commit': geonode_version['commit']
        }, {
            'name': 'GeoServer',
            'website': 'http://geoserver.org/',
            'repo': 'https://github.com/geoserver/geoserver',
            'boundless_repo': 'https://github.com/boundlessgeo/geoserver',
            'version': geoserver_version['version'],
            'commit': geoserver_version['commit']
        }, {
            'name': 'MapLoom',
            'website': 'http://prominentedge.com/projects/maploom.html',
            'repo': 'https://github.com/ROGUE-JCTD/MapLoom',
            'boundless_repo': 'https://github.com/boundlessgeo/' +
                              'django-exchange-maploom',
            'version': maploom_version['version'],
            'commit': maploom_version['commit']
        }, {
            'name': 'OSGeo Importer',
            'repo': 'https://github.com/GeoNode/django-osgeo-importer',
            'version': importer_version['version'],
            'commit': importer_version['commit']
        }, {
            'name': 'React Viewer',
            'website': 'http://client.geonode.org',
            'repo': 'https://github.com/GeoNode/geonode-client',
            'version': react_version['version'],
            'commit': react_version['commit']
        }]

        mobile_installed = "geonode_anywhere" in settings.INSTALLED_APPS
        mobile = (
            mobile_installed and
            # check that the OAuth application has been created
            len(Application.objects.filter(name='Anywhere')) > 0
        )

        current_site = get_current_site(request)

        capabilites = {'site_name': current_site.name,
                       'versions': projects,
                       'mobile': mobile}

        return Response(capabilites)
