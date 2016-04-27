import os
from PIL import Image
from django.test import TestCase
from django.db import IntegrityError
from django.db import transaction
from django.core.files.uploadedfile import SimpleUploadedFile
from exchange.core.models import (SiteName, TagLine, BannerImage, IconImage,
                                  LogoImage, NavbarColor)
workpath = os.path.dirname(os.path.abspath(__file__))
global_fixtures = ['./fixtures/boundless.json']


class ImageAssetTestHelper:
    fixtures = global_fixtures

    """
    ImageAssetTestHelper provides helper methods for testing uploaded
    singleton images.

    args:
      AssetClass: model to be tested
      assetProperty: name of property in the model that takes the uploaded file
      as an argument
    """

    def __init__(self, AssetClass, assetProperty):
        self.AssetClass = AssetClass
        self.assetProperty = assetProperty

    def uploadAsset(self):
        img_0 = open(os.path.join(workpath, 'test_data/test_img.jpg'))
        uploaded_0 = SimpleUploadedFile('asset_0', img_0.read())
        asset_0 = self.AssetClass()
        setattr(asset_0, self.assetProperty, uploaded_0)
        asset_0.save()

    def replaceAsset(self):
        img_0 = open(os.path.join(workpath, 'test_data/test_img.jpg'))
        uploaded_0 = SimpleUploadedFile('asset_0', img_0.read())
        asset_0 = self.AssetClass()
        setattr(asset_0, self.assetProperty, uploaded_0)
        asset_0.save()
        img_1 = open(os.path.join(workpath, 'test_data/test_img.jpg'))
        uploaded_1 = SimpleUploadedFile('asset_1', img_1.read())
        asset_1 = self.AssetClass()
        setattr(asset_1, self.assetProperty, uploaded_1)
        asset_1.save()
        return asset_1


class SiteNameTestCase(TestCase):
    fixtures = global_fixtures

    """Site name should be a singleton"""

    def test_creating_second_title_should_produce_integrity_error(self):
        with self.assertRaises(IntegrityError):
            SiteName.objects.create(site_name="Test Name 1")


class TagLineTestCase(TestCase):
    fixtures = global_fixtures

    """Tag line should be a singleton"""

    def test_creating_second_tagline_should_produce_integrity_error(self):
        with self.assertRaises(IntegrityError):
            TagLine.objects.create(tag_line="Test Tag Line 1")


class BannerImageTestCase(TestCase):
    fixtures = global_fixtures

    """Banner image should upload successfully"""

    def test_should_upload_successfully(self):
        assetTester = ImageAssetTestHelper(BannerImage, 'banner_image')
        assetTester.uploadAsset()
        self.assertEqual(BannerImage.objects.count(), 1)

    """Uploading a second banner image should replace the first banner image"""

    def test_uploading_second_image_should_replace_first(self):
        assetTester = ImageAssetTestHelper(BannerImage, 'banner_image')
        new_asset = assetTester.replaceAsset()
        self.assertEqual(BannerImage.objects.count(), 1)
        self.assertEqual(BannerImage.objects.all()[0], new_asset)


class IconImageTestCase(TestCase):
    fixtures = global_fixtures

    """Icon image should upload successfully"""

    def test_should_upload_successfully(self):
        assetTester = ImageAssetTestHelper(IconImage, 'icon_image')
        assetTester.uploadAsset()
        self.assertEqual(IconImage.objects.count(), 1)

    """Uploading a second icon image should replace the first icon image"""

    def test_uploading_second_image_should_replace_first(self):
        assetTester = ImageAssetTestHelper(IconImage, 'icon_image')
        new_asset = assetTester.replaceAsset()
        self.assertEqual(IconImage.objects.count(), 1)
        self.assertEqual(IconImage.objects.all()[0], new_asset)


class LogoImageTestCase(TestCase):
    fixtures = global_fixtures

    """Icon image should upload successfully"""

    def test_should_upload_successfully(self):
        assetTester = ImageAssetTestHelper(LogoImage, 'logo_image')
        assetTester.uploadAsset()
        self.assertEqual(LogoImage.objects.count(), 1)

    """Uploading a second icon image should replace the first icon image"""

    def test_uploading_second_image_should_replace_first(self):
        assetTester = ImageAssetTestHelper(LogoImage, 'logo_image')
        new_asset = assetTester.replaceAsset()
        self.assertEqual(LogoImage.objects.count(), 1)
        self.assertEqual(LogoImage.objects.all()[0], new_asset)
