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

import logging

from urllib import unquote, urlencode
# noinspection PyCompatibility
from urlparse import parse_qsl

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from wsgiref import util as wsgiref_util

from .ssl_adapter import https_request

logger = logging.getLogger(__name__)


@login_required
def pki_request(request, resource_url=None):
    """
    App's main view
    :param request: Django request object
    :type request: django.http.HttpRequest
    :param resource_url: Remainder of parsed path, e.g. '/pki/<resource_url>'
    :rtype: HttpResponse
    """

    if resource_url is None:
        return HttpResponse('Resource URL missing for PKI request',
                            status=400,
                            content_type='text/plain')

    # TODO: Limit to localhost calls, e.g. when coming from local Py packages

    # Manually copy over headers, skipping unwanted ones
    # IMPORTANT: Don't pass any cookies or OAuth2 headers to remote resource
    headers = {}
    if request.method in ("POST", "PUT") and "CONTENT_TYPE" in request.META:
        headers["Content-Type"] = request.META["CONTENT_TYPE"]

    # Strip our bearer token header!
    auth_header = request.META.get('HTTP_AUTHORIZATION', None)
    # TODO: Passing a bearer token for a remote service should be considered;
    #       add a comparison of our get_bearer_token(), delete only on match
    if auth_header and 'bearer' in auth_header.lower():
        del request.META['HTTP_AUTHORIZATION']

    # Strip our bearer token token from query params!
    # TODO: Migrate to request.GET QueryDict parsing?
    #       Unsure if keep_blank_values and doseq are supported
    query_str = request.META['QUERY_STRING']
    query = None
    if query_str != '':
        # Keep keys with empty values and maintain order
        params = parse_qsl(query_str.strip(), keep_blank_values=True)
        clean_params = [(k, v) for k, v in params if
                        k.lower() != 'access_token']
        query = urlencode(clean_params, doseq=True)

    # Turn the remainder of path back into original URL
    r_url = unquote(resource_url)
    # NOTE: Since no origin scheme is recorded (could be in rewritten pki
    # proxy path), assume https
    url = 'https://' + r_url + (('?' + query) if query else '')

    # Do remote request
    # TODO: Add option to pass a bearer token (but not ours for OAuth2!)
    req_res = https_request(url, data=request.body,
                            method=request.method, headers=headers)
    """:type: requests.Response"""

    if not req_res:
        return HttpResponse('Remote service did not return content.',
                            status=400,
                            content_type='text/plain')

    # TODO: Capture errors and signal to web UI for reporting to user.
    #       Don't let errors just raise exceptions

    if 'Content-Type' in req_res.headers:
        content_type = req_res.headers['Content-Type']
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
        response['Location'] = req_res.headers['Location']
    else:
        response = HttpResponse(
            content=req_res.content,
            status=req_res.status_code,
            reason=req_res.reason,
            content_type=content_type,
        )

    # TODO: Should we be sniffing encoding/charset and passing back?

    # Passthru headers from remote service, but don't overwrite defined headers
    skip_headers = ['content-type']  # add any as lowercase
    for h, v in req_res.headers.items():
        if h.lower() not in skip_headers \
                and not wsgiref_util.is_hop_by_hop(h)\
                and h not in response:
            response[h] = v

    return response
