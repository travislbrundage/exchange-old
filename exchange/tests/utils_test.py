from . import ExchangeTest
import mock
import json
import pytest


class DefaultMapConfigTest(ExchangeTest):

    def mock_proxy_route():
        return True

    @pytest.mark.skip(reason="The mock_proxy_route is not done correctly")
    @mock.patch("exchange.pki.models.uses_proxy_route",
                side_effect=mock_proxy_route)
    @mock.patch("geonode.services.serviceprocessors.base.settings",
                autospec=True)
    def test_proxy_base_map(self, mock_settings, mock_proxy_route):
        mock_settings.PROXY_BASEMAP = True
        from geonode.utils import default_map_config
        map_config, base_layers = default_map_config(None)
        self.assertTrue(json.loads(base_layers[0].source_params)['use_proxy'])
