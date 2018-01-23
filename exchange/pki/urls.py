from django.conf.urls import patterns, url
from .views import test_page

urlpatterns = patterns(
    '',
    url(r'^pki/test', test_page, name='test-page'),)
