from osgeo_importer.handlers import ImportHandlerMixin
from osgeo_importer.handlers import ensure_can_run
from osgeo_importer.inspectors import OGRInspector
from osgeo_importer.utils import database_schema_name
from django import db
from django.conf import settings
import ogr

ogr.UseExceptions()


class OGRPhotoFieldAdder(OGRInspector):
    # Adds additional field to a table
    def add_photo_field(self, layer_name):
        target_layer = self.data.GetLayerByName(layer_name)
        if target_layer.GetLayerDefn().GetFieldIndex('photos') >= 0:
            return None
        target_layer.CreateField(ogr.FieldDefn('photos', ogr.OFTString))
        return 'photos'


class PhotosFieldHandler(ImportHandlerMixin):
    """
    Adds a text field 'photos' to a layer for Anywhere
    """

    adder = OGRPhotoFieldAdder

    def can_run(self, layer, layer_config, *args, **kwargs):
        if 'add_photos' in layer_config and layer_config['add_photos'] is True:
            return True
        return False

    @ensure_can_run
    def handle(self, layer, layer_config, *args, **kwargs):
        d = db.connections[settings.OSGEO_DATASTORE].settings_dict
        connection_string = "PG:dbname='%s' user='%s' " \
            "password='%s' host='%s' " \
            "port='%s' schemas=%s" % (
                d['NAME'], d['USER'],
                d['PASSWORD'], d['HOST'],
                d['PORT'],
                database_schema_name()
            )

        with self.adder(connection_string) as datasource:
            return datasource.add_photo_field(layer)
