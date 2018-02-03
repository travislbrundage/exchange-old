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
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from geonode.services import enumerations
from django.contrib.auth.decorators import login_required
from geonode.services.forms import CreateServiceForm
from .forms import CreatePKIServiceForm

logger = logging.getLogger(__name__)


def test_page(request):
    return render(request, 'test.html')


class CreatePKIServiceForm(CreateServiceForm):
    super(CreatePKIServiceForm)


@login_required
def register_service(request):
    # This method suffers the same as the form's clean() override
    # There is no easy way to inject our custom template and form
    service_register_template = "services/service_register.html"
    if request.method == "POST":
        form = CreatePKIServiceForm(request.POST)
        if form.is_valid():
            service_handler = form.cleaned_data["service_handler"]
            service = service_handler.create_geonode_service(
                owner=request.user)
            service.full_clean()
            service.save()
            service.keywords.add(*service_handler.get_keywords())
            service.set_permissions(
                {'users': {
                    ''.join(request.user.username):
                        ['services.change_service', 'services.delete_service']
                }})
            if service_handler.indexing_method == enumerations.CASCADED:
                service_handler.create_cascaded_store()
            request.session[service_handler.url] = service_handler
            logger.debug("Added handler to the session")
            messages.add_message(
                request,
                messages.SUCCESS,
                _("Service registered successfully")
            )
            result = HttpResponseRedirect(
                reverse("harvest_resources",
                        kwargs={"service_id": service.id})
            )
        else:
            result = render(request, service_register_template, {"form": form})
    else:
        form = CreatePKIServiceForm()
        result = render(
            request, service_register_template, {"form": form})
    return result
