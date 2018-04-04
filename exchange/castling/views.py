
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from geonode.utils import resolve_object
from geonode.documents.models import Document


def index(request):
    dev = settings.CASTLING_DEV
    html = 'castling/index_dev.html' if dev is True else 'castling/index.html'
    return render(request, html, {
        'CASTLING_BUILD_DIR': '.',
    })


def config(request):
    config = {
        'access_token': request.session['access_token'],
        'geoserver_url': '/geoserver',
    }

    return JsonResponse(config)


# Get the details for a document and turn
# them in to a JSON object.
#
def get_document(request, docid):
    # get the document by the doc name.
    doc = resolve_object(request, Document, {'pk': docid},
                         permission='base.view_resourcebase',
                         permission_msg='Access denied')

    # convert the document into a dictionary
    doc_dict = {
        'title': doc.title,
        'date': doc.date.strftime('%Y-%m-%d'),
        'date_type': doc.date_type,
        'bbox_string': doc.bbox_string,
        'bbox_x0': doc.bbox_x0,
        'bbox_x1': doc.bbox_x1,
        'bbox_y0': doc.bbox_y0,
        'bbox_y1': doc.bbox_y1,
        'content_type': doc.content_type,
        'extension': doc.extension,
        'links': [],
    }

    return JsonResponse(doc_dict)
