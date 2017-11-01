# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Completely rebuilds the search index by removing the old data and then updating."

    def add_arguments(self, parser):
        '''
        TODO: Implement any optional arguments to add here which get passed
        to clear_index or update_index
        '''
        return

    def handle(self, **options):
        call_command('clear_index', **options)
        call_command('update_index', **options)
