from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^pki', 'geonode.maps.views.new_map',
        {'template': 'maps/maploom.html'}, name='maploom-map-new'),)
