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
from ordered_model.admin import OrderedModelAdmin

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
    form = SslConfigAdminForm
    fieldsets = (
        (None, {
            'fields': (
                'name',
                'description',
                'ca_custom_certs',
                'ca_allow_invalid_certs',
                'client_cert',
                'client_key',
                'client_key_pass',
                'ssl_verify_mode',
            )
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': (
                'ssl_version',
                'ssl_options',
                'ssl_ciphers',
                'https_retries',
                'https_redirects'
            ),
        }),
    )


class HostnamePortSslConfigAdminForm(forms.ModelForm):
    class Meta:
        model = HostnamePortSslConfig
        fields = '__all__'


class HostnamePortSslConfigAdmin(OrderedModelAdmin):
    list_display = ('enabled', 'hostname_port',
                    'ssl_config', 'move_up_down_links')
    list_display_links = ('hostname_port',)
    list_filter = ('enabled',)
    # list_editable = ('enabled',)
    form = HostnamePortSslConfigAdminForm
    actions = ['enable_mapping', 'disable_mapping']

    def enable_mapping(self, request, queryset):
        up = queryset.count()
        for m in queryset:
            m.enabled = True
            m.save(update_fields=['enabled'])
        self.message_user(
            request,
            "{0} mapping{1} enabled.".format(up, 's' if up > 1 else '')
        )

    def disable_mapping(self, request, queryset):
        up = queryset.count()
        for m in queryset:
            m.enabled = False
            m.save(update_fields=['enabled'])
        self.message_user(
            request,
            "{0} mapping{1} disabled.".format(up, 's' if up > 1 else '')
        )

    enable_mapping.short_description = "Enable selected mappings"
    disable_mapping.short_description = "Disable selected mappings"


admin.site.register(SslConfig,
                    SslConfigAdmin)
admin.site.register(HostnamePortSslConfig,
                    HostnamePortSslConfigAdmin)
