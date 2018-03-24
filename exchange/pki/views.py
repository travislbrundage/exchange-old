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

from geonode.api.views import get_client_ip
from geonode.services import enumerations

from .ssl_session import https_client

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

    # Limit to localhost calls, e.g. when coming from local Py packages
    req_ip = get_client_ip(request)
    logger.debug("req_ip: {0}".format(req_ip))
    allowed_ips = ['127.0.0.1', '[::1]']
    if req_ip not in allowed_ips:
        return HttpResponse(
            "IP address requesting PKI proxy service is not of local origin.",
            status=403,
            content_type="text/plain"
        )

    if not resource_url:
        return HttpResponse('Resource URL missing for PKI request',
                            status=400,
                            content_type='text/plain')

    # Manually copy over headers, skipping unwanted ones
    logger.debug("pki request.COOKIES: {0}".format(request.COOKIES))
    logger.debug("pki request.META: {0}".format(request.META))
    # IMPORTANT: Don't pass any cookies or OAuth2 headers to remote resource
    headers = {}
    if request.method in ("POST", "PUT") and "CONTENT_TYPE" in request.META:
        headers["Content-Type"] = request.META["CONTENT_TYPE"]

    # Pass through HTTP_ACCEPT* headers
    accepts = [
        'Accept', 'Accept-Encoding', 'Accept-Language']
    # Why no support for Accept-Charset, i.e. no HTTP_ACCEPT_CHARSET?
    http_accepts = [
        'HTTP_ACCEPT', 'HTTP_ACCEPT_ENCODING', 'HTTP_ACCEPT_LANGUAGE']
    for accept, http_accept in zip(accepts, http_accepts):
        if http_accept in request.META:
            headers[accept] = request.META[http_accept]

    service_type = request.META['PKI_SERVICE_TYPE'] \
        if 'PKI_SERVICE_TYPE' in request.META else None
    if service_type == enumerations.REST or '/arcgis' in unquote(resource_url):
        # TODO: [FIXME] Workaround for decompression error in arcrest,
        #       in arcrest.web._base._chunk()
        # Needed for both /proxy reroutes and arcrest pkg
        headers['Accept-Encoding'] = ''

    # TODO: Passthru HTTP_REFERER?

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
    logger.debug("pki requests request headers: {0}".format(headers))
    req_res = https_client.request(
        method=request.method,
        url=url,
        headers=headers,
        data=request.body,
    )
    """:type: requests.Response"""

    if not req_res:
        return HttpResponse('Remote service did not return content.',
                            status=400,
                            content_type='text/plain')

    # TODO: Capture errors and signal to web UI for reporting to user.
    #       Don't let errors just raise exceptions

    logger.debug("pki requests response headers:\n{0}".format(req_res.headers))

    if query and 'f=pjson' in query:
        # Sometimes arcrest servers doesn't return proper content type
        content_type = 'application/json'
    elif 'Content-Type' in req_res.headers:
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
        # logger.debug("pki requests response content (first 2000 chars):\n{0}"
        #              .format(req_res.content[:2000]))
        txt_content = 'Not textual content'
        txt_types = ['text', 'json', 'xml']
        if any([t in content_type.lower() for t in txt_types]):
            txt_content = req_res.content
        logger.debug("pki requests response content:\n{0}"
                     .format(txt_content))

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

    logger.debug("pki django response headers:\n{0}"
                 .format(response.serialize_headers()))

    return response
