# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Freshens the index for the given app(s)."

    def handle(self, **options):
        '''
        TOOD: Implement update_index
        '''
        return
