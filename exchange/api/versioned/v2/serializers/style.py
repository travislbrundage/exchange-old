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
import json
from rest_framework import serializers
from geonode.layers.models import Style

logger = logging.getLogger(__name__)


class StyleSerializer(serializers.ModelSerializer):

    def validate(self, data):

        if data['name']:
            data['name'] = (data['name'].lower().replace(" ", "_"))

        if 'mbstyle' in data['format'].lower():
            if data['body']:
                try:
                    mbstyle_doc = json.loads(data['body'])
                except Exception as e:
                    msg = "%s of field body" % e.message
                    raise serializers.ValidationError(msg)

                if "version" not in mbstyle_doc or mbstyle_doc['version'] != 8:
                    if data['version'] and data['version'] == "8":
                        mbstyle_doc['version'] = int(data['version'])
                        data['body'] = json.dumps(mbstyle_doc)
                    else:
                        msg = "Style specification version number. Must be 8."
                        raise serializers.ValidationError(msg)

            else:
                msg = "MBStyle document is invalid."
                raise serializers.ValidationError(msg)

        return data

    class Meta:
        model = Style
        fields = '__all__'
