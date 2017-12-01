# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

from django.core.management.base import BaseCommand
from django.conf import settings
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from exchange.elasticsearchapp.search import LayerIndex, \
    MapIndex, DocumentIndex, ProfileIndex, GroupIndex, StoryIndex
from exchange.layers.models import Layer
from exchange.maps.models import Map
from exchange.documents.models import Document
from exchange.people.models import Profile
from exchange.groups.models import GroupProfile
from exchange.storyscapes.models.base import Story


class Command(BaseCommand):
    help = "Freshens the index for the given app(s)."

    def handle(self, **options):
        '''
        Repopulates the index in elastic.
        '''
        # Is there a way of doing this more programmatically rather
        # than calling each index/model?
        es = Elasticsearch(settings.ES_URL)
        LayerIndex.init()
        MapIndex.init()
        DocumentIndex.init()
        ProfileIndex.init()
        GroupIndex.init()
        StoryIndex.init()

        body = {
            'analysis': {
                'analyzer': 'snowball'
            }
        }
        es.indices.put_settings(body, index='', ignore=400)

        bulk(client=es, actions=(index.indexing() for index in Layer.objects.all().iterator()))
        bulk(client=es, actions=(index.indexing() for index in Map.objects.all().iterator()))
        bulk(client=es, actions=(index.indexing() for index in Document.objects.all().iterator()))
        bulk(client=es, actions=(index.indexing() for index in Profile.objects.all().iterator()))
        bulk(client=es, actions=(index.indexing() for index in GroupProfile.objects.all().iterator()))
        bulk(client=es, actions=(index.indexing() for index in Story.objects.all().iterator()))
