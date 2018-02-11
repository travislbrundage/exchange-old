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

from django import forms
from django.core.exceptions import ValidationError

from exchange.utils import append_access_token
from geonode.services.forms import CreateServiceForm
from geonode.services import enumerations
from geonode.services.serviceprocessors import get_service_handler

from .models import SslConfig, HostnamePortSslConfig
from .utils import pki_route


class CreatePKIServiceForm(CreateServiceForm):
    # In addition to normal service registration,
    # we want to be able to associate it with an SslConfig model
    ssl_config = forms.ModelChoiceField(
        queryset=SslConfig.objects.none(),
        empty_label="Select custom configuration...",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        """:type: from django.http import HttpRequest"""
        super(CreatePKIServiceForm, self).__init__(*args, **kwargs)
        self.fields['ssl_config'].queryset = \
            SslConfig.objects.default_and_all()

    def clean_url(self):
        # Here we can add our own validation if necessary
        return super(CreatePKIServiceForm, self).clean_url()

    def clean(self):
        # Unfortunately we have to override and redo the function
        # In order to inject the pki rerouting
        url = self.cleaned_data.get("url")
        service_type = self.cleaned_data.get("type")
        save_url = None

        if url is not None and url.lower().startswith('https'):
            ssl_config = self.cleaned_data.get("ssl_config")
            if ssl_config is not None:
                HostnamePortSslConfig.objects.create_hostnameportsslconfig(
                    url, ssl_config
                )
                url = pki_route(url)
                save_url = url
                url = append_access_token(url, request=self.request)

        if url is not None and service_type is not None:
            try:
                service_handler = get_service_handler(
                    base_url=url, service_type=service_type)
            except Exception, e:
                raise ValidationError(
                    "Could not connect to the service at %(url)s\n%(trace)s",
                    params={"url": url, "trace": repr(e)}
                )
            if not service_handler.has_resources():
                raise ValidationError(
                    "Could not find importable resources for the service " +
                    "at %(url)s",
                    params={"url": url}
                )
            elif service_type not in (enumerations.AUTO, enumerations.OWS):
                if service_handler.service_type != service_type:
                    raise ValidationError(
                        "Found service of type %(found_type)s instead " +
                        "of %(service_type)s",
                        params={
                            "found_type": service_handler.service_type,
                            "service_type": service_type
                        }
                    )
            service_handler.url = save_url or url
            self.cleaned_data["service_handler"] = service_handler
            self.cleaned_data["type"] = service_handler.service_type
