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
from .forms import CreatePKIServiceForm
from urllib import unquote
from .utils import requests_base_url
from requests import get, Session, ConnectionError
from django.http import HttpResponse
from .ssl_adapter import SslContextAdapter, get_ssl_context_opts

logger = logging.getLogger(__name__)


def test_page(request):
    return render(request, 'test.html')


@login_required
def register_service(request):
    # This method suffers the same as the form's clean() override
    # There is no easy way to inject our custom template and form
    service_register_template = "service_pki_register.html"
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
                "Service registered successfully"
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


# This represents the pki app's view
def pki_request(request, resource_url=None):
    """
    :param resource_url:
    :rtype: HttpResponse
    """

    # skip Django request passing for now
    # skip Django path manipulation for now (just pass full URL for this test)

    # needed if SslContextAdapter internal normalization causes issues
    # url = normalize_hostname(resource_url)
    url = 'https://' + unquote(resource_url)
    base_url = requests_base_url(resource_url)

    req_ses = Session()  # type: requests.Session

    # IMPORTANT: base_url is (scheme://hostname:port), not full url.
    # Note: urllib3 (as of 1.22) seems to care about case when matching the
    # hostname to the peer server's SSL cert, in contrast to the spec, which
    # says such matches should be case-insensitive (this is a bug):
    #   https://tools.ietf.org/html/rfc5280#section-4.2.1.6
    #   https://tools.ietf.org/html/rfc6125 <-- best practices
    req_ses.mount(base_url, SslContextAdapter(*get_ssl_context_opts(base_url)))
    # TODO: Passthru Django request headers, cookies, etc.
    # Should we be sending cookies from project's domain into remote endpoint?
    req_res = req_ses.get(url)
    """:type: requests.Response"""
    # TODO: Capture errors and signal to web UI for reporting to user.
    #       Don't let errors just raise exceptions

    # TODO: Passthru requests headers, cookies, etc.
    # Should we be setting cookies in project's domain from remote endpoint?
    # TODO: Should we be sniffing encoding/charset and passing back?
    response = HttpResponse(
        content=req_res.content,
        status=req_res.status_code,
        reason=req_res.reason,
        content_type=req_res.headers.get('Content-Type'),
    )

    return response
