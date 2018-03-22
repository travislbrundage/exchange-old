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

import logging
from exchange.api.base import views as base_views
from . import serializers as v2_serializers
from rest_framework import viewsets, status

from rest_framework.response import Response
from geonode.layers.models import Style, Attribute
from geonode.services.models import Service

from exchange.core.backends.legacy import GeonodeMapServiceBackend


logger = logging.getLogger(__name__)


class LayerViewSet(base_views.LayerViewSet):
    serializer_class = v2_serializers.LayerSerializer


class CategoryViewSet(base_views.CategoryViewSet):
    serializer_class = v2_serializers.CategorySerializer


class AttributeViewSet(viewsets.ModelViewSet):
    queryset = Attribute.objects.all()
    serializer_class = v2_serializers.AttributeSerializer
    http_method_names = ['get', 'put', 'head', 'options']


class StyleViewSet(viewsets.ModelViewSet):
    queryset = Style.objects.all()
    serializer_class = v2_serializers.StyleSerializer
    lookup_field = 'name'


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = v2_serializers.ServiceSerializer
    lookup_field = 'name'


class MapViewSet(viewsets.ViewSet):
    serializer_class = v2_serializers.MapSerializer
    service = GeonodeMapServiceBackend()

    def list(self, request):
        records = self.service.search_records(owner=request.user)
        serializer = v2_serializers.MapSerializer(
            instance=records,
            many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = v2_serializers.MapSerializer(data=request.data)
        if serializer.is_valid():
            record = self.service.create_record(
                serializer.save(), owner=request.user)
            return Response(record,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            map = self.service.get_record(pk, owner=request.user)
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = v2_serializers.MapSerializer(instance=map)
        return Response(serializer.data)

    def update(self, request, pk=None):

        try:
            map = self.service.get_record(pk)
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = v2_serializers.MapSerializer(
            data=request.data, instance=map)
        if serializer.is_valid():
            self.service.update_record(
                serializer.save(), owner=request.user)
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        try:
            map = self.service.get_record(pk)
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = v2_serializers.MapSerializer(
            data=request.data,
            instance=map,
            partial=True)
        if serializer.is_valid():
            map = self.service.update_record(
                serializer.save(), pk=pk, owner=request.user)
            return Response(map,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            self.service.remove_record(pk)
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)
