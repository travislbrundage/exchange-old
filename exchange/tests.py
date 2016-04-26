from django.test import TestCase
from django.db import IntegrityError
from django.db import transaction
from django.core.files.uploadedfile import SimpleUploadedFile
from exchange.models import SiteName, TagLine, BannerImage, IconImage, LogoImage, NavbarColor

class SiteNameTestCase(TestCase):
    def test_creating_second_title_should_produce_integrity_error(self):
        SiteName.objects.create(site_name="Test Name 0")
        with self.assertRaises(IntegrityError):
            SiteName.objects.create(site_name="Test Name 1")

class TagLineTestCase(TestCase):
    def test_creating_second_tagline_should_produce_integrity_error(self):
        TagLine.objects.create(tag_line="Test Tag Line 0")
        with self.assertRaises(IntegrityError):
            TagLine.objects.create(tag_line="Test Tag Line 1")

class BannerImageCase(TestCase):

    def test_add_photo(self):
        banner = BannerImage()
        banner.image = SimpleUploadedFile(name='test_image.jpg', content="test image content", content_type='image/jpeg')
        banner.save()
        self.assertEqual(Photo.objects.count(), 1)

##    def test_creating_second_banner_should_produce_integrity_error(self):
##        banner = BannerImage()
##        banner.image = SimpleUploadedFile(name='test_image2.jpg', content=open(image_path, 'rb').read(), content_type='image/jpeg')
##        banner2 = BannerImage()
##        with self.assertRaises(IntegrityError):
##            banner.image = SimpleUploadedFile(name='test_image2.jpg', content=open(self.TEST_ROOT + 'test_image2.jpg', 'rb').read(), content_type='image/jpeg')
