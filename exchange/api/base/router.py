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

from . import views
from rest_framework import routers

router = routers.DefaultRouter()

router.register(r'categories', views.CategoryViewSet,
                base_name="categories")
router.register(r'layers', views.LayerViewSet,
                base_name="layers")
router.register(r'capabilities', views.CapabilitiesViewSet,
                base_name="capabilities")

api_urlpatterns = router.urls
