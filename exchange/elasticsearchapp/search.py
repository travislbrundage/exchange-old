from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import DocType, Integer, Text, Boolean, Date, Float
from django.contrib.contenttypes.models import ContentType
from agon_ratings.models import OverallRating
from dialogos.models import Comment
from django.conf import settings
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch

connections.create_connection(hosts=[settings.ES_URL])


class LayerIndex(DocType):
    id = Integer()
    abstract = Text()
    category__gn_description = Text()
    csw_type = Text()
    csw_wkt_geometry = Text()
    detail_url = Text()
    owner__username = Text()
    owner__first_name = Text()
    owner__last_name = Text()
    is_published = Boolean()
    featured = Boolean()
    popular_count = Integer()
    share_count = Integer()
    rating = Integer()
    srid = Text()
    supplemental_information = Text()
    thumbnail_url = Text()
    uuid = Text()
    title = Text()
    date = Date()
    type = Text()
    subtype = Text()
    typename = Text()
    title_sortable = Text()
    category = Text()
    bbox_left = Float()
    bbox_right = Float()
    bbox_bottom = Float()
    bbox_top = Float()
    temporal_extent_start = Date()
    temporal_extent_end = Date()
    keywords = Text(multi=True)
    regions = Text(multi=True)
    num_ratings = Integer()
    num_comments = Integer()
    geogig_link = Text()
    has_time = Boolean()

    class Meta:
        index = 'layer-index'


class MapIndex(DocType):
    id = Integer()
    abstract = Text()
    category__gn_description = Text()
    csw_type = Text()
    csw_wkt_geometry = Text()
    detail_url = Text()
    owner__username = Text()
    popular_count = Integer()
    share_count = Integer()
    rating = Integer()
    srid = Text()
    supplemental_information = Text()
    thumbnail_url = Text()
    uuid = Text()
    title = Text()
    date = Date()
    type = Text()
    title_sortable = Text()
    category = Text()
    bbox_left = Float()
    bbox_right = Float()
    bbox_bottom = Float()
    bbox_top = Float()
    temporal_extent_start = Date()
    temporal_extent_end = Date()
    keywords = Text(multi=True)
    regions = Text(multi=True)
    num_ratings = Integer()
    num_comments = Integer()

    class Meta:
        index = 'map-index'


class DocumentIndex(DocType):
    id = Integer()
    abstract = Text()
    category__gn_description = Text()
    csw_type = Text()
    csw_wkt_geometry = Text()
    detail_url = Text()
    owner__username = Text()
    popular_count = Integer()
    share_count = Integer()
    rating = Integer()
    srid = Text()
    supplemental_information = Text()
    thumbnail_url = Text()
    uuid = Text()
    title = Text()
    date = Date()
    type = Text()
    title_sortable = Text()
    category = Text()
    bbox_left = Float()
    bbox_right = Float()
    bbox_bottom = Float()
    bbox_top = Float()
    temporal_extent_start = Date()
    temporal_extent_end = Date()
    keywords = Text(multi=True)
    regions = Text(multi=True)
    num_ratings = Integer()
    num_comments = Integer()

    class Meta:
        index = 'document-index'


class ProfileIndex(DocType):
    id = Integer()
    username = Text()
    first_name = Text()
    last_name = Text()
    profile = Text()
    organization = Text()
    position = Text()
    type = Text()

    class Meta:
        index = 'profile-index'


class GroupIndex(DocType):
    id = Integer()
    title = Text()
    title_sortable = Text()
    description = Text()
    json = Text()
    type = Text()

    class Meta:
        index = 'group-index'


class StoryIndex(DocType):
    id = Integer()
    abstract = Text()
    category__gn_description = Text()
    distribution_description = Text()
    distribution_url = Text()
    owner__username = Text()
    popular_count = Integer()
    share_count = Integer()
    rating = Integer()
    thumbnail_url = Text()
    detail_url = Text()
    uuid = Text()
    title = Text()
    date = Date()
    type = Text()
    title_sortable = Text()
    category = Text()
    bbox_left = Float()
    bbox_right = Float()
    bbox_bottom = Float()
    bbox_top = Float()
    temporal_extent_start = Date()
    temporal_extent_end = Date()
    keywords = Text(multi=True)
    regions = Text(multi=True)
    num_ratings = Integer()
    num_comments = Integer()
    num_chapters = Integer()
    owner__first_name = Text()
    owner__last_name = Text()
    is_published = Boolean()
    featured = Boolean()

    class Meta:
        index = 'story-index'
