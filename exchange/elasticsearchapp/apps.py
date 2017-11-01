from django.apps import AppConfig


class ElasticsearchappConfig(AppConfig):
    name = 'exchange.elasticsearchapp'

    def ready(self):
        import exchange.elasticsearchapp.signals
