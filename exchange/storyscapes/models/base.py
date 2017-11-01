from geonode.base.models import ResourceBase, TopicCategory
from geonode.maps.models import Map
import json
import uuid

from django import core, db
from django.utils.translation import ugettext_lazy as _
from exchange.elasticsearchapp.search import StoryIndex


class Story(ResourceBase):

    chapters = db.models.ManyToManyField(Map, through='StoryChapter')

    def get_absolute_url(self):
        return core.urlresolvers.reverse('story_detail', None, [str(self.id)])

    def update_from_viewer(self, conf):

        if isinstance(conf, basestring):
            conf = json.loads(conf)

        self.title = conf['title']
        self.abstract = conf['abstract']
        self.is_published = conf['is_published']
        self.detail_url = self.get_absolute_url()
        if conf['category'] is not None:
            self.category = TopicCategory(conf['category'])

        if self.uuid is None or self.uuid == '':
            self.uuid = str(uuid.uuid1())

        removed_chapter_ids = conf['removed_chapters']
        if removed_chapter_ids is not None and len(removed_chapter_ids) > 0:
            for chapter_id in removed_chapter_ids:
                chapter_obj = StoryChapter.objects.get(map_id=chapter_id)
                self.chapters.get(storychapter=chapter_obj).delete()

        #self.keywords.add(*conf['map'].get('keywords', []))
        self.save()

    def viewer_json(self, user):

        about = {
            'title': self.title,
            'abstract': self.abstract,
            'owner': self.owner.name_long,
            'username': self.owner.username
        }

        config = {
            'id': self.id,
            'about': about,
            'chapters': [chapter.map.viewer_json(user, None) for chapter in self.chapters.all()],
            'thumbnail_url': '/static/geonode/img/missing_thumb.png'
        }

        return config

    def update_thumbnail(self, first_chapter_obj):
        if first_chapter_obj.chapter_index != 0:
            return

        chapter_base = ResourceBase.objects.get(id=first_chapter_obj.id)
        ResourceBase.objects.filter(id=self.id).update(
            thumbnail_url=chapter_base.thumbnail_url
        )

    @property
    def class_name(self):
        return self.__class__.__name__


    distribution_url_help_text = _(
        'information about on-line sources from which the dataset, specification, or '
        'community profile name and extended metadata elements can be obtained')
    distribution_description_help_text = _(
        'detailed text description of what the online resource is/does')
    distribution_url = db.models.TextField(
        _('distribution URL'),
        blank=True,
        null=True,
        help_text=distribution_url_help_text)
    distribution_description = db.models.TextField(
        _('distribution description'),
        blank=True,
        null=True,
        help_text=distribution_description_help_text)

    class Meta(ResourceBase.Meta):
        verbose_name_plural = 'Stories'
        db_table = 'maps_story'
        pass

    # elasticsearch_dsl indexing
    def indexing(self):
        obj = StoryIndex(
            meta={'id': self.id},
            id=self.id,
            abstract=self.abstract,
            # TODO: Does this work? It's a resourcebase_api field?
            category__gn_description=self.category__gn_description,
            distribution_description=self.distribution_description,
            distribution_url=self.distribution_url,
            detail_url=self.detail_url,
            owner__username=self.owner,
            # TODO: Do these work for grabbing the fields of owner?
            owner__first_name=self.owner__first_name,
            owner__last_name=self.owner__last_name,
            is_published=self.is_published,
            featured=self.featured,
            popular_count=self.popular_count,
            share_count=self.share_count,
            rating=self.prepare_rating(),
            thumbnail_url=self.thumbnail_url,
            uuid=self.uuid,
            title=self.title,
            date=self.date,
            type=self.prepare_type(),
            title_sortable=self.prepare_title_sortable(),
            # TODO: Does this work for grabbing the fields of category?
            category=self.category__identifier,
            bbox_left=self.bbox_x0,
            bbox_right=self.bbox_x1,
            bbox_bottom=self.bbox_y0,
            bbox_top=self.bbox_y1,
            temporal_extent_start=self.temporal_extent_start,
            temporal_extent_end=self.temporal_extent_end,
            # TODO: Does this need to be a function call?
            keywords=self.keyword_slug_list,
            # TODO: Does this need to be a function call?
            regions=self.region_name_list,
            num_ratings=self.prepare_num_ratings(),
            num_comments=self.prepare_num_comments(),
            num_chapters=self.prepare_num_chapters()
        )
        obj.save()
        return obj.to_dict(include_meta=True)

    # elasticsearch_dsl indexing helper functions
    def prepare_type(self):
        return "story"

    def prepare_rating(self):
        ct = ContentType.objects.get_for_model(self)
        try:
            rating = OverallRating.objects.filter(
                object_id=self.pk,
                content_type=ct
            ).aggregate(r=Avg("rating"))["r"]
            return float(str(rating or "0"))
        except OverallRating.DoesNotExist:
            return 0.0

    def prepare_num_ratings(self):
        ct = ContentType.objects.get_for_model(self)
        try:
            return OverallRating.objects.filter(
                object_id=self.pk,
                content_type=ct
            ).all().count()
        except OverallRating.DoesNotExist:
            return 0

    def prepare_num_comments(self):
        ct = ContentType.objects.get_for_model(self)
        try:
            return Comment.objects.filter(
                object_id=self.pk,
                content_type=ct
            ).all().count()
        except:
            return 0

    def prepare_title_sortable(self):
        return self.title.lower()

    def prepare_num_chapters(self):
        try:
            return self.chapters.all().count()
        except:
            return 0


class StoryChapter(db.models.Model):
    story = db.models.ForeignKey(Story, blank=True, null=True)
    map = db.models.ForeignKey(Map, blank=True, null=True)
    chapter_index = db.models.IntegerField(_('chapter index'), null=True, blank=True)
    viewer_playbackmode = db.models.CharField(_('Viewer Playback'), max_length=32, blank=True, null=True)

    #This needs review

    def update_from_viewer(self, conf):

        if isinstance(conf, basestring):
            conf = json.loads(conf)

        self.viewer_playbackmode = conf['viewer_playbackmode'] or 'Instant'

        self.chapter_index = conf['chapter_index']
        story_id = conf.get('story_id', 0)
        story_obj = Story.objects.get(id=story_id)
        self.story = story_obj
        self.save()

    #def viewer_json(self, user, access_token=None, *added_layers): access_token, *added_
    #    base_config = super(Map, self).viewer_json(user,layers)
    #    base_config['viewer_playbackmode'] = self.viewer_playbackmode
    #    base_config['tools'] = [{'outputConfig': {'playbackMode': self.viewer_playbackmode}, 'ptype': 'gxp_playback'}]

    #    return base_config

    class Meta(ResourceBase.Meta):
        verbose_name_plural = 'Chapters'
        db_table = 'maps_story_bridge'
        pass

