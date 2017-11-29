from . import ExchangeTest


@pytest.mark.skipif(settings.ES_UNIFIED_SEARCH is False,
                    reason="Only run if using unified search")
class ElasticsearchappTest(ExchangeTest):

    def setUp(self):
        super(ElasticsearchappTest, self).setup()
        self.login()

    def test_thing(self):
        # TODO: Implement relevant tests for the elasticsearchapp
        return
