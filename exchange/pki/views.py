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

from urllib import unquote, urlencode
# noinspection PyCompatibility
from urlparse import parse_qs

from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from wsgiref import util as wsgiref_util

from geonode.services import enumerations

from .forms import CreatePKIServiceForm
from .ssl_adapter import https_request

logger = logging.getLogger(__name__)


@login_required
def register_service(request):
    # This method suffers the same as the form's clean() override
    # There is no easy way to inject our custom template and form
    service_register_template = "service_pki_register.html"
    if request.method == "POST":
        form = CreatePKIServiceForm(request.POST, request=request)
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
        form = CreatePKIServiceForm(request=request)
        result = render(
            request, service_register_template, {"form": form})
    return result


def pki_request(request, resource_url=None):
    """
    App's main view
    :param request: Django request object
    :param resource_url: Remainder of parsed path, e.g. '/pki/<resource_url>'
    :rtype: HttpResponse
    """

    # Culled from geonode.api.views.get_client_ip()
    # x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    # if x_forwarded_for:
    #     ip = x_forwarded_for.split(',')[0]
    # else:
    #     ip = request.META.get('REMOTE_ADDR')
    # TODO: Finish allowed proxy origination IP support; restrict by IP

    # Manually copy over headers, skipping unwanted ones
    # IMPORTANT: Don't pass any OAuth2 headers or cookies to remote resource
    headers = {}
    if request.method in ("POST", "PUT") and "CONTENT_TYPE" in request.META:
        headers["Content-Type"] = request.META["CONTENT_TYPE"]

    # Strip any oauth2 token from query params!
    query_str = request.META['QUERY_STRING']
    query = None
    if query_str != '':
        params = parse_qs(query_str.strip(), keep_blank_values=True)
        if 'access_token' in params:
            del params['access_token']
        query = urlencode(params, doseq=True)

    # TODO: strip OAuth2 header as well

    # Turn the remainder of path back into original URL
    r_url = unquote(resource_url)
    # NOTE: Since no origin scheme is recorded (could be in rewritten pki
    # proxy path), assume https
    url = 'https://' + r_url + (('?' + query) if query else '')

    # Do remote request
    # TODO: add option to pass a bearer token (but not ours for OAuth2!)
    req_res = https_request(url, data=request.body,
                            method=request.method, headers=headers)
    """:type: requests.Response"""

    if not req_res:
        return HttpResponse(status=400,
                            content='Remote service did not return content.')

    # TODO: Capture errors and signal to web UI for reporting to user.
    #       Don't let errors just raise exceptions

    if 'Content-Type' in req_res.headers:
        content_type = req_res.headers.get('Content-Type')
    else:
        content_type = 'text/plain'

    # If we get a redirect, beyond # allowed in config, add a useful message.
    if req_res.status_code in (301, 302, 303, 307):
        response = HttpResponse(
            'This proxy does not support more than the configured redirects. '
            'The server in "{0}" asked for this recent redirect: "{1}"'
            .format(url, req_res.headers.get('Location')),
            status=req_res.status_code,
            content_type=content_type
        )
    else:
        response = HttpResponse(
            content=req_res.content,
            status=req_res.status_code,
            reason=req_res.reason,
            content_type=content_type,
        )

    # TODO: Should we be sniffing encoding/charset and passing back?

    # Passthru headers from remote service
    skip_headers = ['Content-Type']
    for h, v in req_res.headers.items():
        if h not in skip_headers and not wsgiref_util.is_hop_by_hop(h):
            response[h] = v

    return response
