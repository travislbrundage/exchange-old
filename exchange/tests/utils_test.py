from . import ExchangeTest
import mock


class DefaultMapConfigTest(ExchangeTest):

    def mock_proxy_route():
        return True

    # TODO: Mocking done correctly?
    @mock.patch("exchange.pki.models.uses_proxy_route",
                side_effect=mock_proxy_route)
    @mock.patch("geonode.services.serviceprocessors.base.settings",
                autospec=True)
    def test_proxy_base_map(self, mock_settings, mock_proxy_route):
        mock_settings.PROXY_BASEMAP = True
        from geonode.utils import default_map_config
        map_config, base_layers = default_map_config(None)
        # TODO: Correct way to access use_proxy variable?
        self.assertTrue(base_layers[0].source_params['use_proxy'])
