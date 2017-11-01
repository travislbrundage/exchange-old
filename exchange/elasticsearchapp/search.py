from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import DocType, Integer, String, Boolean, Date, Float
from django.contrib.contenttypes.models import ContentType
from agon_ratings.models import OverallRating
from dialogos.models import Comment
from django.conf import settings
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch

connections.create_connection(hosts=[settings.ES_URL])


class LayerIndex(DocType):
    id = Integer()
    abstract = String()
    category__gn_description = String()
    csw_type = String()
    csw_wkt_geometry = String()
    detail_url = String()
    owner__username = String()
    owner__first_name = String()
    owner__last_name = String()
    is_published = Boolean()
    featured = Boolean()
    popular_count = Integer()
    share_count = Integer()
    rating = Integer()
    srid = String()
    supplemental_information = String()
    thumbnail_url = String()
    uuid = String()
    title = String()
    date = Date()
    type = String()
    subtype = String()
    typename = String()
    title_sortable = String()
    category = String()
    bbox_left = Float()
    bbox_right = Float()
    bbox_bottom = Float()
    bbox_top = Float()
    temporal_extent_start = Date()
    temporal_extent_end = Date()
    keywords = String(multi=True)
    regions = String(multi=True)
    num_ratings = Integer()
    num_comments = Integer()
    geogig_link = String()
    has_time = Boolean()

    class Meta:
        index = 'layer-index'


class MapIndex(DocType):
    id = Integer()
    abstract = String()
    category__gn_description = String()
    csw_type = String()
    csw_wkt_geometry = String()
    detail_url = String()
    owner__username = String()
    popular_count = Integer()
    share_count = Integer()
    rating = Integer()
    srid = String()
    supplemental_information = String()
    thumbnail_url = String()
    uuid = String()
    title = String()
    date = Date()
    type = String()
    title_sortable = String()
    category = String()
    bbox_left = Float()
    bbox_right = Float()
    bbox_bottom = Float()
    bbox_top = Float()
    temporal_extent_start = Date()
    temporal_extent_end = Date()
    keywords = String(multi=True)
    regions = String(multi=True)
    num_ratings = Integer()
    num_comments = Integer()

    class Meta:
        index = 'map-index'


class DocumentIndex(DocType):
    id = Integer()
    abstract = String()
    category__gn_description = String()
    csw_type = String()
    csw_wkt_geometry = String()
    detail_url = String()
    owner__username = String()
    popular_count = Integer()
    share_count = Integer()
    rating = Integer()
    srid = String()
    supplemental_information = String()
    thumbnail_url = String()
    uuid = String()
    title = String()
    date = Date()
    type = String()
    title_sortable = String()
    category = String()
    bbox_left = Float()
    bbox_right = Float()
    bbox_bottom = Float()
    bbox_top = Float()
    temporal_extent_start = Date()
    temporal_extent_end = Date()
    keywords = String(multi=True)
    regions = String(multi=True)
    num_ratings = Integer()
    num_comments = Integer()

    class Meta:
        index = 'document-index'


class ProfileIndex(DocType):
    id = Integer()
    username = String()
    first_name = String()
    last_name = String()
    profile = String()
    organization = String()
    position = String()
    type = String()

    class Meta:
        index = 'profile-index'


class GroupIndex(DocType):
    id = Integer()
    title = String()
    title_sortable = String()
    description = String()
    json = String()
    type = String()

    class Meta:
        index = 'group-index'


class StoryIndex(DocType):
    id = Integer()
    abstract = String()
    category__gn_description = String()
    distribution_description = String()
    distribution_url = String()
    owner__username = String()
    popular_count = Integer()
    share_count = Integer()
    rating = Integer()
    thumbnail_url = String()
    detail_url = String()
    uuid = String()
    title = String()
    date = Date()
    type = String()
    title_sortable = String()
    category = String()
    bbox_left = Float()
    bbox_right = Float()
    bbox_bottom = Float()
    bbox_top = Float()
    temporal_extent_start = Date()
    temporal_extent_end = Date()
    keywords = String(multi=True)
    regions = String(multi=True)
    num_ratings = Integer()
    num_comments = Integer()
    num_chapters = Integer()
    owner__first_name = String()
    owner__last_name = String()
    is_published = Boolean()
    featured = Boolean()

    class Meta:
        index = 'story-index'
