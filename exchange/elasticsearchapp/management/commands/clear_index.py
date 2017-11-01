# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Clears out the search index completely."

    def handle(self, **options):
        '''
        TOOD: Implement clear_index
        Clears out the search index completely.
        '''
        self.stdout.write("Removing all documents from your index.")
        # clear call
