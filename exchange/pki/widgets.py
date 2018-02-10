from django.forms.widgets import Widget
from django.template import loader
from django.utils.safestring import mark_safe
from .models import SslConfig
import json


class SelectPKIWidget(Widget):
    template_name = 'pki_select.html'

    def get_context(self, name, value, attrs=None):
        all_configs = [x for x in SslConfig.objects.all()]

        return {'widget': {
            'name': name,
            'value': value,
            'ssl_configs': all_configs,
            #'ssl_configs2': json.dumps({'data': [x.to_ssl_config() for x in SslConfig.objects.all()]}),
        }}

    def render(self, name, value, attrs=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)
