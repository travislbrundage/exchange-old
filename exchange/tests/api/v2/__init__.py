# -*- coding: utf-8 -*-
citeGroup = '''{"version": 8,
        "name": "citeGroup",
  "center": [0,0],
  "zoom": 7,
  "sources": {
    "cite": {
      "type": "vector",
      "tiles": [
        "http://localhost:8080/geoserver/gwc/service/wmts?REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0&LAYER=citeGroup&STYLE=&TILEMATRIX=EPSG:900913:{z}&TILEMATRIXSET=EPSG:900913&FORMAT=application/x-protobuf;type=mapbox-vector&TILECOL={x}&TILEROW={y}"
      ],
      "minZoom": 0,
      "maxZoom": 14
    }
  },
  "layers": [
    {
      "type": "background",
      "id": "background",
      "paint": {
        "background-color": "#E3E3E9"
      }
    },
    {
      "type": "fill",
      "id": "fill",
      "source": "cite",
      "source-layer": "Lakes",
      "paint": {
        "fill-color": "#C3C3C3",
        "fill-opacity": 0.9
      }
    },
    {
      "type": "line",
      "id": "line",
      "source": "cite",
      "source-layer": "BasicPolygons",
      "paint": {
        "line-color": "#777777",
        "line-width": 1,
        "line-dasharray": [4, 4]
      }
    },
    {
      "type": "symbol",
      "id": "names",
      "source": "cite",
      "source-layer": "NamedPlaces",
      "layout": {
        "text-field": "{Name}",
        "text-size": 14,
        "text-font": ["Open Sans"],
        "text-max-width": 100
      },
      "paint": {
        "text-color": "#333333"
      }
    }
  ]
}'''

error_map_json = '''{"id": 1, "version": 8,
"name": "my_first_mccccajpffffd","center":[-92.99999999999999,45],
"zoom":10,"bearing":0,"metadata":{"bnd:layer-version":9,
"bnd:source-version":3},"sources":{"osm":{"type":"raster",
"tileSize":256,"tiles":["https://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
"https://b.tile.openstreetmap.org/{z}/{x}/{y}.png",
"https://c.tile.openstreetmap.org/{z}/{x}/{y}.png"]},
"minnesota_tracts":{"type":"vectors",
"url":"/geoserver/gwc/service/tms/1.0.0/cite:minnesota_tracts@EPSG%3A3857@pbf/{z}/{x}/{-y}.pbf"},
"minnesota_bus_shelters":{"type":"vector",
"url":"/geoserver/gwc/service/tms/1.0.0/cite:minnesota_bus_shelters@EPSG%3A3857@pbf/{z}/{x}/{-y}.pbf"}},
"layers":[{"filter":null,"paint":{},
"metadata":{},"id":"osm", "type":"background",
"source":"osm"},
{"filter":null,"paint":{"fill-color":"#417692",
"fill-opacity":1,"fill-outline-color":"#5b48be"},
"metadata":{},"id":"minnesota_tracts",
"source":"minnesota_tracts","type":"fill",
"source-layer":"minnesota_tracts",
"layout":{"visibility":"visible"}},{"filter":null,
"paint":{"text-field":"",
"text-font":["FontAwesome Normal"],"text-color":"#f8e71c"},
"metadata":{},"id":"minnesota_bus_shelters",
"source":"minnesota_bus_shelters",
"type":"symbol","source-layer":"minnesota_bus_shelters",
"layout":{"visibility":"visible",
"text-field":"","text-font":["FontAwesome Normal"]}}]}'''
