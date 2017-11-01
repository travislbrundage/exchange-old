# TODO: Make sure these import correctly
from geonode.layers.models import Layer
from geonode.maps.models import Map
from geonode.documents.models import Document
from geonode.people.models import Profile
from geonode.groups.models import GroupProfile
from exchange.storyscapes.models.base import Story
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Layer)
def layer_index_post(sender, instance, **kwargs):
    instance.indexing()


@receiver(post_save, sender=Map)
def map_index_post(sender, instance, **kwargs):
    instance.indexing()


@receiver(post_save, sender=Document)
def document_index_post(sender, instance, **kwargs):
    instance.indexing()


@receiver(post_save, sender=Profile)
def profile_index_post(sender, instance, **kwargs):
    instance.indexing()


@receiver(post_save, sender=GroupProfile)
def group_index_post(sender, instance, **kwargs):
    instance.indexing()


@receiver(post_save, sender=Story)
def story_index_post(sender, instance, **kwargs):
    instance.indexing()
