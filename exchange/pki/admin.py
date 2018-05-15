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

import warnings
import datetime

from six import StringIO

from django.conf.urls import url
from django.contrib import admin, messages
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from ordered_model.admin import OrderedModelAdmin
from django.utils.safestring import mark_safe

from .models import SslConfig, HostnamePortSslConfig, SslLogEntry
from .validate import PkiValidationWarning
from . import ssl_messages


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

    def changeform_view(self, request, object_id=None, form_url='',
                        extra_context=None):

        if request.method == 'POST':
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always", category=PkiValidationWarning)
                tmpl_resp = super(SslConfigAdmin, self).changeform_view(
                    request,
                    object_id=object_id,
                    form_url=form_url,
                    extra_context=extra_context)

            if len(w) > 0:
                # noinspection PyProtectedMember
                sslconfig_verbose_name = SslConfig._meta.verbose_name
                warn = w[0].message
                if isinstance(warn, PkiValidationWarning):
                    msg = warn.message_html_pre()
                else:
                    msg = str(warn)
                self.message_user(
                    request,
                    mark_safe(u"Last saved {0} validation warnings:<br>{1}"
                              .format(sslconfig_verbose_name, msg)),
                    messages.WARNING)

            return tmpl_resp
        else:
            return super(SslConfigAdmin, self).changeform_view(
                request,
                object_id=object_id,
                form_url=form_url,
                extra_context=extra_context)


class HostnamePortSslConfigAdminForm(forms.ModelForm):
    class Meta:
        model = HostnamePortSslConfig
        fields = '__all__'


class HostnamePortSslConfigAdmin(OrderedModelAdmin):
    list_display = ('enabled', 'hostname_port',
                    'ssl_config', 'proxy', 'move_up_down_links')
    list_display_links = ('hostname_port', 'ssl_config',)
    list_filter = ('enabled', 'proxy',)
    # list_editable = ('enabled',)
    form = HostnamePortSslConfigAdminForm
    actions = [
        'enable_mapping', 'disable_mapping',
        'enable_proxy', 'disable_proxy'
    ]

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

    def enable_proxy(self, request, queryset):
        up = queryset.count()
        for m in queryset:
            m.proxy = True
            m.save(update_fields=['proxy'])
        self.message_user(
            request,
            "{0} mapping{1} proxy enabled.".format(up, 's' if up > 1 else '')
        )

    def disable_proxy(self, request, queryset):
        up = queryset.count()
        for m in queryset:
            m.proxy = False
            m.save(update_fields=['proxy'])
        self.message_user(
            request,
            "{0} mapping{1} proxy disabled.".format(up, 's' if up > 1 else '')
        )

    enable_proxy.short_description = "Enable proxy for selected mappings"
    disable_proxy.short_description = "Disable proxy for selected mappings"


class SslLogEntryAdminForm(forms.ModelForm):
    class Meta:
        model = SslLogEntry
        fields = '__all__'


class SslLogEntryAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'level', 'message')
    list_display_links = ('timestamp',)
    list_filter = ('level',)
    readonly_fields = ('timestamp', 'level', 'message')
    form = SslLogEntryAdminForm

    actions = [
        'export_entries',
    ]

    def get_urls(self):
        cur_urls = super(SslLogEntryAdmin, self).get_urls()
        urlpatterns = [
            url(r'^enable-log/$',
                self.admin_site.admin_view(self.enable_log),
                name="enable_log"
                ),
            url(r'^disable-log/$',
                self.admin_site.admin_view(self.disable_log),
                name="disable_log"
                ),
            url(r'^clear-log/$',
                self.admin_site.admin_view(self.clear_log),
                name="clear_log"),
            url(r'^export-log/$',
                self.admin_site.admin_view(self.export_log),
                name="export_log"),
        ]
        return urlpatterns + cur_urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        log_messages = ssl_messages.get('log')
        extra_context['ssl_log_enabled'] = \
            log_messages is not None and log_messages
        return super(SslLogEntryAdmin, self).changelist_view(
            request, extra_context=extra_context)

    def has_add_permission(self, request):
        return False

    def enable_log(self, request):
        if ssl_messages.get('log') is not None:
            ssl_messages['log'] = True
            self.message_user(
                request,
                "IMPORTANT: Enable debug logging only for "
                "VERY SHORT PERIODS OF TIME.",
                messages.WARNING
            )
        else:
            self.message_user(
                request,
                "Could not enable debug logging.",
                messages.WARNING
            )
        return HttpResponseRedirect("../")

    def disable_log(self, request):
        if ssl_messages.get('log') is not None:
            ssl_messages['log'] = False
        else:
            self.message_user(
                request,
                "Could not disable debug logging.",
                messages.WARNING
            )
        return HttpResponseRedirect("../")

    def clear_log(self, request):
        SslLogEntry.objects.all().delete()
        self.message_user(
            request,
            "Debug log cleared."
        )
        return HttpResponseRedirect("../")

    @staticmethod
    def message_log_download(queryset):
        # reorder in chronological order (newest last, like a log file)
        msgs = [u"{0}\n".format(m.message) for m in reversed(queryset)]

        f = StringIO()
        f.writelines(msgs)
        f.seek(0)
        tstamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        response = HttpResponse(
            f, content_type='text/plain', charset='utf-8')
        response['Content-Disposition'] = \
            'attachment; filename=ssl-debug-output_{0}.log'.format(tstamp)
        return response

    def export_log(self, request):
        queryset = SslLogEntry.objects.all()
        if queryset:
            return self.message_log_download(queryset)
        else:
            self.message_user(
                request,
                "No log messages found to export.",
                messages.WARNING
            )
        return HttpResponseRedirect("../")

    def export_entries(self, request, queryset):
        if queryset:
            return self.message_log_download(queryset)
        else:
            self.message_user(
                request,
                "No log messages found to export.",
                messages.WARNING
            )

    export_entries.short_description = "Export selected entries"


admin.site.register(SslConfig,
                    SslConfigAdmin)
admin.site.register(HostnamePortSslConfig,
                    HostnamePortSslConfigAdmin)
admin.site.register(SslLogEntry,
                    SslLogEntryAdmin)
