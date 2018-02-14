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

from django.contrib import admin
from django import forms

from .models import SslConfig, HostnamePortSslConfig


class SslConfigAdminForm(forms.ModelForm):
    class Meta:
        model = SslConfig
        fields = '__all__'
        widgets = {
            'client_key_pass': forms.PasswordInput(render_value=True),
        }


class SslConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'ssl_version', 'ssl_verify_mode')
    list_display_links = ('id', 'name',)
    list_filter = ('id', 'name',)
    form = SslConfigAdminForm


class HostnamePortSslConfigAdminForm(forms.ModelForm):
    class Meta:
        model = HostnamePortSslConfig
        fields = '__all__'


class HostnamePortSslConfigAdmin(admin.ModelAdmin):
    list_display = ('hostname_port', 'ssl_config')
    list_display_links = ('hostname_port',)
    list_filter = ('hostname_port',)
    form = HostnamePortSslConfigAdminForm


admin.site.register(SslConfig,
                    SslConfigAdmin)
admin.site.register(HostnamePortSslConfig,
                    HostnamePortSslConfigAdmin)
