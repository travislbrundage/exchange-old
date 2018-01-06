from . import ExchangeTest
from elasticsearch_dsl import connections
from django.conf import settings
from elasticsearch import Elasticsearch
import pytest
from django.core.management import call_command
import subprocess


@pytest.mark.skipif(settings.ES_SEARCH is False,
                    reason="Only run if using unified search")
class GeonodeElasticsearchTest(ExchangeTest):

    def setUp(self):
        super(GeonodeElasticsearchTest, self).setUp()
        self.login()
        call_command('rebuild_index')
        # connect to the ES instance
        connections.create_connection(hosts=[settings.ES_URL])

    def test_management_commands(self):
        es = Elasticsearch(settings.ES_URL)
        mappings = es.indices.get_mapping()

        # Ensure all the indices exist in our mappings upon build
        self.assertTrue('profile-index' in mappings)
        self.assertTrue('layer-index' in mappings)
        self.assertTrue('map-index' in mappings)
        self.assertTrue('document-index' in mappings)
        self.assertTrue('group-index' in mappings)
        self.assertTrue('story-index' in mappings)

        # Call the clear command and ensure the indices have been wiped
        call_command('clear_index')
        mappings = es.indices.get_mapping()
        self.assertFalse('profile-index' in mappings)
        self.assertFalse('layer-index' in mappings)
        self.assertFalse('map-index' in mappings)
        self.assertFalse('document-index' in mappings)
        self.assertFalse('group-index' in mappings)
        self.assertFalse('story-index' in mappings)

        # Rebuild the indices and ensure they return to our mappings
        call_command('rebuild_index')
        mappings = es.indices.get_mapping()
        self.assertTrue('profile-index' in mappings)
        self.assertTrue('layer-index' in mappings)
        self.assertTrue('map-index' in mappings)
        self.assertTrue('document-index' in mappings)
        self.assertTrue('group-index' in mappings)
        self.assertTrue('story-index' in mappings)

    def test_mappings(self):
        # We only want to test mappings because the rest should be covered
        # in the views_test.py for faceting and filtering
        es = Elasticsearch(settings.ES_URL)
        mappings = es.indices.get_mapping()

        profile_mappings = mappings[
            'profile-index']['mappings']['doc']['properties']
        profile_properties = {
            "profile": {
                "type": "keyword"
            },
            "username": {
                "type": "text"
            },
            "first_name": {
                "type": "text"
            },
            "last_name": {
                "type": "text"
            },
            "position": {
                "type": "keyword"
            },
            "organization": {
                "type": "text"
            },
            "type": {
                "type": "keyword"
            },
            "id": {
                "type": "integer"
            }
        }
        print profile_mappings
        print profile_properties
        self.assertDictEqual(profile_mappings, profile_properties)

        group_mappings = mappings[
            'group-index']['mappings']['doc']['properties']
        group_properties = {
            "description": {
                "type": "text"
            },
            "title": {
                "type": "text",
                "analyzer" : "simple"
            },
            "title_sortable": {
                "type": "text",
                "analyzer" : "simple"
            },
            "json": {
                "type": "text"
            },
            "type": {
                "type": "keyword"
            },
            "id": {
                "type": "integer"
            }
        }
        self.assertDictEqual(group_mappings, group_properties)

        document_mappings = mappings[
            'document-index']['mappings']['doc']['properties']
        document_properties = {
            "rating": {
                "type": "integer"
            },
            "category__gn_description": {
                "type": "text"
            },
            "abstract": {
                "type": "text"
            },
            "bbox_bottom": {
                "type": "float"
            },
            "num_ratings": {
                "type": "integer"
            },
            "date": {
                "type": "date"
            },
            "keywords": {
                "type": "keyword"
            },
            "detail_url": {
                "type": "keyword"
            },
            "id": {
                "type": "integer"
            },
            "category": {
                "type": "keyword"
            },
            "uuid": {
                "type": "keyword"
            },
            "title": {
                "type": "text",
                "analyzer" : "simple"
            },
            "num_comments": {
                "type": "integer"
            },
            "title_sortable": {
                "type": "text",
                "analyzer" : "simple"
            },
            "regions": {
                "type": "text"
            },
            "share_count": {
                "type": "integer"
            },
            "type": {
                "type": "keyword"
            },
            "bbox_top": {
                "type": "float"
            },
            "popular_count": {
                "type": "integer"
            },
            "bbox_right": {
                "type": "float"
            },
            "srid": {
                "type": "keyword"
            },
            "temporal_extent_end": {
                "type": "date"
            },
            "supplemental_information": {
                "type": "text"
            },
            "bbox_left": {
                "type": "float"
            },
            "thumbnail_url": {
                "type": "keyword"
            },
            "csw_type": {
                "type": "keyword"
            },
            "csw_wkt_geometry": {
                "type": "keyword"
            },
            "owner__username": {
                "type": "keyword"
            },
            "temporal_extent_start": {
                "type": "date"
            }
        }
        self.assertDictEqual(document_mappings, document_properties)

        layer_mappings = mappings[
            'layer-index']['mappings']['doc']['properties']
        layer_properties = {
            "rating": {
                "type": "integer"
            },
            "owner__last_name": {
                "type": "text"
            },
            "has_time": {
                "type": "boolean"
            },
            "category__gn_description": {
                "type": "text"
            },
            "abstract": {
                "type": "text"
            },
            "bbox_bottom": {
                "type": "float"
            },
            "num_ratings": {
                "type": "integer"
            },
            "srid": {
                "type": "keyword"
            },
            "featured": {
                "type": "boolean"
            },
            "keywords": {
                "type": "keyword"
            },
            "detail_url": {
                "type": "keyword"
            },
            "id": {
                "type": "integer"
            },
            "category": {
                "type": "keyword"
            },
            "uuid": {
                "type": "keyword"
            },
            "title": {
                "type": "text",
                "analyzer" : "simple"
            },
            "num_comments": {
                "type": "integer"
            },
            "title_sortable": {
                "type": "text",
                "analyzer" : "simple"
            },
            "regions": {
                "type": "text"
            },
            "share_count": {
                "type": "integer"
            },
            "type": {
                "type": "keyword"
            },
            "geogig_link": {
                "type": "keyword"
            },
            "bbox_top": {
                "type": "float"
            },
            "popular_count": {
                "type": "integer"
            },
            "bbox_right": {
                "type": "float"
            },
            "date": {
                "type": "date"
            },
            "owner__first_name": {
                "type": "text"
            },
            "temporal_extent_end": {
                "type": "date"
            },
            "supplemental_information": {
                "type": "text"
            },
            "bbox_left": {
                "type": "float"
            },
            "typename": {
                "type": "keyword"
            },
            "subtype": {
                "type": "keyword"
            },
            "thumbnail_url": {
                "type": "keyword"
            },
            "csw_type": {
                "type": "keyword"
            },
            "csw_wkt_geometry": {
                "type": "keyword"
            },
            "owner__username": {
                "type": "keyword"
            },
            "temporal_extent_start": {
                "type": "date"
            },
            "is_published": {
                "type": "boolean"
            }
        }
        self.assertDictEqual(layer_mappings, layer_properties)

        map_mappings = mappings[
            'map-index']['mappings']['doc']['properties']
        map_properties = {
            "rating": {
                "type": "integer"
            },
            "category__gn_description": {
                "type": "text"
            },
            "abstract": {
                "type": "text"
            },
            "bbox_bottom": {
                "type": "float"
            },
            "num_ratings": {
                "type": "integer"
            },
            "date": {
                "type": "date"
            },
            "keywords": {
                "type": "keyword"
            },
            "detail_url": {
                "type": "keyword"
            },
            "id": {
                "type": "integer"
            },
            "category": {
                "type": "keyword"
            },
            "uuid": {
                "type": "keyword"
            },
            "title": {
                "type": "text",
                "analyzer" : "simple"
            },
            "num_comments": {
                "type": "integer"
            },
            "title_sortable": {
                "type": "text",
                "analyzer" : "simple"
            },
            "regions": {
                "type": "text"
            },
            "share_count": {
                "type": "integer"
            },
            "type": {
                "type": "keyword"
            },
            "bbox_top": {
                "type": "float"
            },
            "popular_count": {
                "type": "integer"
            },
            "bbox_right": {
                "type": "float"
            },
            "srid": {
                "type": "keyword"
            },
            "temporal_extent_end": {
                "type": "date"
            },
            "supplemental_information": {
                "type": "text"
            },
            "bbox_left": {
                "type": "float"
            },
            "thumbnail_url": {
                "type": "keyword"
            },
            "csw_type": {
                "type": "keyword"
            },
            "csw_wkt_geometry": {
                "type": "keyword"
            },
            "owner__username": {
                "type": "keyword"
            },
            "temporal_extent_start": {
                "type": "date"
            }
        }
        self.assertDictEqual(map_mappings, map_properties)

        story_mappings = mappings[
            'story-index']['mappings']['doc']['properties']
        story_properties = {
            "rating": {
                "type": "integer"
            },
            "owner__last_name": {
                "type": "text"
            },
            "category__gn_description": {
                "type": "text"
            },
            "abstract": {
                "type": "text"
            },
            "bbox_bottom": {
                "type": "float"
            },
            "num_ratings": {
                "type": "integer"
            },
            "featured": {
                "type": "boolean"
            },
            "keywords": {
                "type": "keyword"
            },
            "detail_url": {
                "type": "keyword"
            },
            "id": {
                "type": "integer"
            },
            "category": {
                "type": "keyword"
            },
            "uuid": {
                "type": "keyword"
            },
            "title": {
                "type": "text",
                "analyzer" : "simple"
            },
            "num_comments": {
                "type": "integer"
            },
            "title_sortable": {
                "type": "text",
                "analyzer" : "simple"
            },
            "regions": {
                "type": "text"
            },
            "num_chapters": {
                "type": "integer"
            },
            "share_count": {
                "type": "integer"
            },
            "type": {
                "type": "keyword"
            },
            "distribution_description": {
                "type": "text"
            },
            "bbox_top": {
                "type": "float"
            },
            "popular_count": {
                "type": "integer"
            },
            "bbox_right": {
                "type": "float"
            },
            "date": {
                "type": "date"
            },
            "owner__first_name": {
                "type": "text"
            },
            "temporal_extent_end": {
                "type": "date"
            },
            "distribution_url": {
                "type": "keyword"
            },
            "bbox_left": {
                "type": "float"
            },
            "thumbnail_url": {
                "type": "keyword"
            },
            "owner__username": {
                "type": "keyword"
            },
            "temporal_extent_start": {
                "type": "date"
            },
            "is_published": {
                "type": "boolean"
            }
        }
        self.assertDictEqual(story_mappings, story_properties)
