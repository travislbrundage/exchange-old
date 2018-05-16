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

from datetime import timedelta
from logging import Handler

from django.apps import apps
from django.utils import timezone

from . import ssl_messages


class SslLogHandler(Handler, object):
    """
    Logs an SslLogEntry model to Django database.
    """

    def __init__(self):
        super(SslLogHandler, self).__init__()

    def emit(self, record):
        try:
            entry_model = apps.get_app_config('pki').get_model('SslLogEntry')
        except LookupError:
            return

        # Check elapse timer; log if still active
        timer_dt = ssl_messages.get('timer', None)
        if timer_dt is not None:
            if timer_dt > timezone.now():
                log_entry = entry_model(
                    level=record.levelname,
                    message=self.format(record)
                )
                log_entry.save()
            else:
                # Elapse the timer
                ssl_messages['timer'] = None

        # Clean up expired log records
        expiry = ssl_messages.get('expiry', 0)
        if expiry > 0:
            entry_model.objects.filter(
                time__lt=timezone.now() - timedelta(seconds=expiry)).delete()
