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
from rest_framework import serializers
from exchange.core.models import Map

logger = logging.getLogger(__name__)


def validate_version(value):
    if value != 8:
        raise serializers.ValidationError(
            'Style specification version number. Must be 8.'
        )


def validate_layers(value):
    layer_props = ['id', 'type']
    layer_types = ['background', 'fill', 'line',
                   'symbol', 'raster', 'circle',
                   'fill-extrusion', 'heatmap', 'hillshade']
    for layer in value:
        if all(key in layer.keys() for key in layer_props):
            if layer['type'] not in layer_types:
                msg = "Incorrect layer type. Expected a " \
                      "one of (%s), but got (%s)" % \
                      (", ".join(layer_types), layer['type'])
                raise serializers.ValidationError({'layers': msg})
            elif layer['type'] != 'background' \
                    and 'source' not in layer.keys():
                msg = "Invalid layer definition for %s. " \
                      "Name of a source is required " \
                      "for all layer types " \
                      "except background." % layer['id']
                raise serializers.ValidationError({'layer.type': msg})
        else:
            msg = "Missing properties. " \
                  "Expected all of (%s), but got (%s)" % \
                  (", ".join(layer_props), ", ".join(layer.keys()))
            raise serializers.ValidationError({'layers': msg})


class MapSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    version = serializers.IntegerField(validators=[validate_version])
    name = serializers.CharField(max_length=256)
    metadata = serializers.DictField(required=False)
    zoom = serializers.FloatField(required=False)
    center = serializers.ListField(child=serializers.FloatField(),
                                   required=False)
    bearing = serializers.IntegerField(default=0, required=False)
    pitch = serializers.IntegerField(default=0, required=False)
    light = serializers.DictField(child=serializers.CharField(),
                                  required=False)
    sources = serializers.DictField(child=serializers.DictField())
    sprite = serializers.CharField(max_length=256, required=False)
    glyphs = serializers.CharField(max_length=256, required=False)
    transition = serializers.DictField(child=serializers.CharField(),
                                       required=False)
    layers = serializers.ListField(
        child=serializers.DictField(), required=False,
        validators=[validate_layers]
    )

    def validate(self, data):

        source_types = ['vector', 'raster',
                        'raster-dem', 'geojson',
                        'image', 'video', 'canvas']
        for k, v in data['sources'].iteritems():
            if v['type'] not in source_types:
                msg = "Incorrect source type. " \
                      "Expected a one of (%s), but got (%s)"
                raise serializers.ValidationError({'sources': msg %
                                                  (", ".join(source_types),
                                                   v['type'])})

        return data

    def create(self, validated_data):
        return Map(**validated_data)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        return instance
