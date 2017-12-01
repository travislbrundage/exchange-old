from exchange.layers.models import Layer
from exchange.maps.models import Map
from exchange.documents.models import Document
from exchange.people.models import Profile
from exchange.groups.models import GroupProfile
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
