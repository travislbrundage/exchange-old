# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

from django.core.management.base import BaseCommand
from django.conf import settings
from elasticsearch import Elasticsearch


class Command(BaseCommand):
    help = "Clears out the search index completely."

    def handle(self, **options):
        '''
        Clears out the search index completely.
        '''
        self.stdout.write("Removing all documents from your index.")
        es = Elasticsearch(settings.ES_URL)
        # Iterate through every index in our elasticsearch endpoint
        for index in es.indices.get_mapping().iteritems():
            es.indices.delete(index=index[0])
