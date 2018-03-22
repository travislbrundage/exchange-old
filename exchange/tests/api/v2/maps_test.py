# -*- coding: utf8 -*-
from exchange.tests import ExchangeTest
from . import citeGroup, error_map_json
from rest_framework import status
from django.core.urlresolvers import reverse
import json


class ViewTestCase(ExchangeTest):
    """Test suite for the api views."""

    def setUp(self):
        """Define the test client and other test variables."""
        super(ViewTestCase, self).setUp()
        self.login(api_client=True)
        self.source_type_error_map_json = json.loads(error_map_json)
        self.map_json = json.loads(citeGroup)

    def test_create_map(self):
        """Test the api has map creation capability."""
        self.response = self.client.post(
            reverse('api-v2:maps-list'),
            "",
            format='json')
        self.assertEqual(self.response.status_code,
                         status.HTTP_400_BAD_REQUEST)

        self.response = self.client.post(
            reverse('api-v2:maps-list'),
            self.map_json,
            format='json')
        self.map_pk = self.response.data['id']
        self.assertEqual(self.response.status_code,
                         status.HTTP_201_CREATED)

    def test_create_map_source_type_error(self):
        """Test the api has map creation capability."""

        self.response = self.client.post(
            reverse('api-v2:maps-list'),
            self.source_type_error_map_json,
            format='json')
        self.assertEqual(self.response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_create_map_version_error(self):
        """Test the api has map creation capability."""
        self.source_type_error_map_json['version'] = 5
        self.response = self.client.post(
            reverse('api-v2:maps-list'),
            self.source_type_error_map_json,
            format='json')
        self.assertEqual(self.response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_create_map_layer_error(self):
        """Test the api has map creation capability."""

        del self.map_json['layers'][1]['source']
        self.response = self.client.post(
            reverse('api-v2:maps-list'),
            self.map_json,
            format='json')
        self.assertEqual(self.response.status_code,
                         status.HTTP_400_BAD_REQUEST)

        self.map_json['layers'][1]['type'] = 'invalid'
        self.response = self.client.post(
            reverse('api-v2:maps-list'),
            self.map_json,
            format='json')
        self.assertEqual(self.response.status_code,
                         status.HTTP_400_BAD_REQUEST)

        del self.map_json['layers'][1]['id']
        self.response = self.client.post(
            reverse('api-v2:maps-list'),
            self.map_json,
            format='json')
        self.assertEqual(self.response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_get_maps(self):
        """Test the api has map retrieval capability."""

        self.response = self.client.get(
            reverse('api-v2:maps-list'),
            format='json')
        self.assertEqual(self.response.status_code,
                         status.HTTP_200_OK)

    def test_get_map(self):
        """Test the api has map retrieval capability."""

        self.response = self.client.post(
            reverse('api-v2:maps-list'),
            self.map_json,
            format='json')
        map_pk = self.response.data['id']

        self.response = self.client.get(
            reverse('api-v2:maps-detail', kwargs={'pk': 4}),
            format='json')
        self.assertEqual(self.response.status_code,
                         status.HTTP_404_NOT_FOUND)

        self.response = self.client.get(
            reverse('api-v2:maps-detail', kwargs={'pk': 'should_be_integer'}),
            format='json')
        self.assertEqual(self.response.status_code,
                         status.HTTP_400_BAD_REQUEST)

        response = self.client.get(
            reverse('api-v2:maps-detail', kwargs={'pk': map_pk}),
            format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_map(self):
        """Test the api has map retrieval capability."""

        self.response = self.client.post(
            reverse('api-v2:maps-list'),
            self.map_json,
            format='json')
        map_pk = self.response.data['id']

        self.response = self.client.put(
            reverse('api-v2:maps-detail', kwargs={'pk': map_pk}),
            "",
            format='json')
        self.assertEqual(self.response.status_code,
                         status.HTTP_400_BAD_REQUEST)

        self.response = self.client.put(
            reverse('api-v2:maps-detail', kwargs={'pk': 4}),
            self.map_json,
            format='json')
        self.assertEqual(self.response.status_code,
                         status.HTTP_404_NOT_FOUND)

        self.response = self.client.put(
            reverse('api-v2:maps-detail', kwargs={'pk': 'should_be_integer'}),
            self.map_json,
            format='json')
        self.assertEqual(self.response.status_code,
                         status.HTTP_400_BAD_REQUEST)

        self.map_json['name'] = 'updated'
        self.response = self.client.put(
            reverse('api-v2:maps-detail', kwargs={'pk': map_pk}),
            self.map_json,
            format='json')
        self.assertEqual(self.response.data['name'], 'updated')
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)

    def test_delete_map(self):
        """Test the api has map retrieval capability."""

        self.response = self.client.delete(
            reverse('api-v2:maps-detail', kwargs={'pk': 'should_be_integer'}))
        self.assertEqual(self.response.status_code,
                         status.HTTP_400_BAD_REQUEST)

        self.response = self.client.delete(
            reverse('api-v2:maps-detail', kwargs={'pk': 4}))
        self.assertEqual(self.response.status_code,
                         status.HTTP_404_NOT_FOUND)
