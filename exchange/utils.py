# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2016 Boundless Spatial
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

import datetime

from oauthlib.common import generate_token
from oauth2_provider.models import AccessToken, get_application_model
from geonode.people.utils import get_default_user

def get_admin_token():
    Application = get_application_model()
    app = Application.objects.get(name="GeoServer")
    token = generate_token()
    AccessToken.objects.get_or_create(
        user=get_default_user(),
        application=app,
        expires=datetime.datetime.now() + datetime.timedelta(days=3),
        token=token)
    return token