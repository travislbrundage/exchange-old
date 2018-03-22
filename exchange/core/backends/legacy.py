import logging
import uuid
from .base import BaseServiceBackend
from geonode.maps.models import Map as GeonodeMap, MapLayer
from exchange.core.models import Map
from django.core.exceptions import ObjectDoesNotExist
try:
    import json
except ImportError:
    from django.utils import simplejson as json

logger = logging.getLogger(__name__)


def _to_layer(model, layer, source, ordering):
    """
    Parse an object out of a parsed layer configuration from viewer.

    ``model`` is the type to instantiate
    ``layer`` is the parsed dict for the layer
    ``source`` is the parsed dict for the layer's source
    ``ordering`` is the index of the layer within the map's layer list
    """
    layer_cfg = dict(layer)
    for k in ["format", "name", "opacity", "styles", "transparent",
              "fixed", "group", "visibility", "getFeatureInfo"]:
        if k in layer_cfg:
            del layer_cfg[k]

    source_cfg = dict(source)
    for k in ["url", "projection"]:
        if k in source_cfg:
            del source_cfg[k]

    return model(
        stack_order=ordering,
        format=layer.get("format", None),
        name=layer.get("name", layer.get("id", None)),
        opacity=layer.get("opacity", 1),
        styles=layer.get("styles", None),
        transparent=layer.get("transparent", False),
        fixed=layer.get("fixed", False),
        group=layer.get('group', None),
        visibility=layer.get("visibility", True),
        ows_url=source.get("url", None),
        layer_params=json.dumps(layer_cfg),
        source_params=json.dumps(source_cfg)
    )


class GeonodeMapServiceBackend(BaseServiceBackend):
    def __init__(self, *args, **kwargs):
        pass

    def __to_domain(self, data):
        def uniqify(seq):
            """
            get a list of unique items from the input sequence.

            This relies only on equality tests, so you can use it on most
            things.  If you have a sequence of hashables, list(set(seq)) is
            better.
            """
            results = []
            for x in seq:
                if x not in results:
                    results.append(x)
            return results

        def get_domain(data):
            layers = list(data.layers)
            sources = {}
            source_configs = [l.source_config('') for l in layers]
            for source in uniqify(source_configs):
                if 'id' in source:
                    id = source['id']
                    del source['id']
                    sources[id] = source
            layer_configs = [l.layer_config() for l in layers]
            domain = {}
            domain['id'] = data.id
            domain['version'] = data.version
            domain['name'] = data.name
            domain['bearing'] = data.bearing
            domain['sprite'] = data.sprite
            domain['glyphs'] = data.glyphs
            domain['pitch'] = data.pitch
            domain['sources'] = sources
            domain['layers'] = layer_configs
            domain['center'] = [data.center_x, data.center_y]
            domain['metadata'] = {'title': data.title,
                                  'abstract': data.abstract}
            return Map(**domain)

        if isinstance(object, (list,)):
            records = []
            for map in data:
                records.append(get_domain(map))
            return records
        else:
            return get_domain(data)

    def get_record(self, pk, owner=None):
        try:
            map = GeonodeMap.objects.get(pk=pk)
            return self.__to_domain(map)
        except ObjectDoesNotExist as e:
            raise KeyError(e.message)

    def search_records(self, limit=None, owner=None, **filters):
        records = []
        for record in GeonodeMap.objects.filter(**filters):
            records.append(self.__to_domain(record))
        return records

    def remove_record(self, pk):
        map = None
        try:
            map = GeonodeMap.objects.get(pk=pk)
        except ObjectDoesNotExist as e:
            raise KeyError(e.message)

        map.delete()

    def update_record(self, item, owner=None):

        map_obj = GeonodeMap.objects.get(pk=item.id)
        map_obj.zoom = item.zoom

        def source_for(layer):
            source = {}
            if layer['type'] != 'background':
                source = item.sources[layer['source']]
                source['id'] = layer['source']
            return source

        if item.name:
            map_obj.name = item.name

        if item.metadata:
            if 'title' in item.metadata:
                map_obj.title = item.metadata['title']

            if 'abstract' in item.metadata:
                map_obj.abstract = item.metadata['abstract']

        if item.layers:
            layers = [l for l in item.layers]

            for layer in map_obj.layer_set.all():
                layer.delete()

            for ordering, layer in enumerate(layers):
                map_obj.layer_set.add(
                    _to_layer(
                        MapLayer, layer, source_for(layer), ordering
                    ))

        map_obj.save()

        return self.__to_domain(map_obj)

    def create_record(self, instance, owner=None):
        map_obj = GeonodeMap(owner=owner, zoom=instance.zoom,
                             center_x=0, center_y=0)

        map_obj.name = instance.name
        map_obj.zoom = instance.zoom
        map_obj.version = instance.version
        map_obj.bearing = instance.bearing
        map_obj.pitch = instance.pitch
        map_obj.sprite = instance.sprite
        map_obj.glyphs = instance.glyphs
        map_obj.center_x = instance.center[0]
        map_obj.center_y = instance.center[1]
        map_obj.save()
        map_obj.set_default_permissions()
        map_obj.abstract = ''
        map_obj.set_bounds_from_center_and_zoom(0, 0, 3)

        if map_obj.uuid is None or map_obj.uuid == '':
            map_obj.uuid = str(uuid.uuid1())

        def source_for(layer):
            source = {}
            if layer['type'] != 'background':
                source = instance.sources[layer['source']]
                source['id'] = layer['source']
            return source

        if instance.metadata:
            if 'title' in instance.metadata:
                map_obj.title = instance.metadata['title']

            if 'abstract' in instance.metadata:
                map_obj.abstract = instance.metadata['abstract']

        if instance.layers:
            layers = [l for l in instance.layers]

            for layer in map_obj.layer_set.all():
                layer.delete()

            for ordering, layer in enumerate(layers):
                map_obj.layer_set.add(
                    _to_layer(
                        MapLayer, layer, source_for(layer), ordering
                    ))

        map_obj.save()

        return {'id': map_obj.id}
