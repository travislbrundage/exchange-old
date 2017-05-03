# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2016 Boundless Spatial
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

from django.db import models
from solo.models import SingletonModel
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from resizeimage import resizeimage
from django import forms
import os
import uuid
import datetime


class ThumbnailImage(SingletonModel):
    thumbnail_image = models.ImageField(
        upload_to=os.path.join(settings.MEDIA_ROOT, 'thumbs'),
    )

    def save(self, *args, **kwargs):
        pil_image_obj = Image.open(self.thumbnail_image)
        new_image = resizeimage.resize_cover(
            pil_image_obj,
            [250, 150],
            validate=False
        )

        new_image_io = BytesIO()
        new_image.save(new_image_io, format='PNG')

        temp_name = self.thumbnail_image.name
        self.thumbnail_image.delete(save=False)

        self.thumbnail_image.save(
            temp_name,
            content=ContentFile(new_image_io.getvalue()),
            save=False
        )

        super(ThumbnailImage, self).save(*args, **kwargs)


class ThumbnailImageForm(forms.Form):
    thumbnail_image = forms.FileField(
        label='Select a file',
    )


class CSWRecord(models.Model):
    # Registry requires a UUID for all new records
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=128, default='Unknown')
    user = models.ForeignKey(
          settings.AUTH_USER_MODEL,
          null=True,
          related_name="csw_records_created")

    category_choices = (
        ('Air', 'Air (Aero)'),
        ('Intelligence', 'Intelligence'),
        ('Elevation', 'Elevation'),
        ('HumanGeog', 'Human Geography'),
        ('Basemaps', 'Basemaps'),
        ('Space', 'Space'),
        ('Land', 'Land (Topo)'),
        ('Targeting', 'Targeting'),
        ('NamesBoundaries', 'Names & Boundaries'),
        ('MapsCharts', 'NGA Standard Maps & Charts'),
        ('Sea', 'Sea (Maritime)'),
        ('Imagery', 'Imagery/Collections'),
        ('Geomatics', 'Geodesy/Geodetics Geomatics'),
        ('Weather', 'Weather')
    )

    classification = models.CharField(max_length=128, blank=True)
    title = models.CharField(max_length=328, blank=False)
    modified = models.DateField(default=datetime.date.today, blank=False)
    # 'agency' is assumed to be distinct from logged-in User here
    agency = models.CharField(max_length=128, blank=True)
    record_type = models.CharField(max_length=128, blank=True)
    alternative = models.CharField(max_length=128, blank=True)
    abstract = models.TextField(blank=True)
    service_endpoint_url = models.URLField(max_length=128, blank=False)
    record_format = models.CharField(max_length=128, blank=True)
    bbox_upper_corner = models.CharField(max_length=128,
                                         default="85.0 180",
                                         blank=True)
    bbox_lower_corner = models.CharField(max_length=128,
                                         default="-85.0 -180",
                                         blank=True)
    contact_email = models.CharField(max_length=128, blank=True)
    contact_phone = models.CharField(max_length=128, blank=True)
    gold = models.BooleanField(max_length=128, default=False, blank=True)
    category = models.CharField(max_length=128, choices=category_choices,
                                blank=True)

    class Meta(object):
        verbose_name = 'CSW Record'
        verbose_name_plural = 'CSW Records'


class CSWRecordForm(forms.ModelForm):
    class Meta:
        model = CSWRecord
        fields = ('service_endpoint_url', 'title', 'modified', 'agency', 'record_type', 
                  'alternative', 'abstract', 'record_format', 'bbox_upper_corner',
                  'bbox_lower_corner', 'contact_email', 'contact_phone', 'gold', 'category')

        labels = {
            'service_endpoint_url': _('Service Endpoint Url'),
            'title': _('Title'),
            'modified': _('Date Last Modified'),
            'agency': _('Agency'),
            'record_type': _('Type'),
            'alternative': _('Alternative'),
            'abstract': _('Abstract'),
            'record_format': _('Format'),
            'bbox_upper_corner': _('Bounding Box: Upper Corner'),
            'bbox_lower_corner': _('Bounding Box: Lower Corner'),
            'contact_email': _('Contact Email'),
            'contact_phone': _('Contact Phone'),
            'gold': _('Gold'),
            'category': _('Category')
        }

        help_texts = {
            'service_endpoint_url': _('e.g. http://example.com/ArcGIS/rest/services/Specialty/ESRI_StateCityHighway_USA/MapServer'),
            # 'title': _('Title'),
            # 'agency': _('Agency'),
            # 'record_type': _('Type'),
            # 'alternative': _('Alternative'),
            # 'abstract': _('Abstract'),
            # 'record_format': _('Format'),
            'bbox_upper_corner': _('Coordinates for upper left corner'),
            'bbox_lower_corner': _('Coordinates for lower right corner'),
            # 'contact_email': _('Contact Email'),
            # 'contact_phone': _('Contact Phone'),
            # 'gold': _('Gold'),
            # 'category': _('Category'),
        }
