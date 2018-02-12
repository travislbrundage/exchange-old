from django.forms.widgets import Select
from django.template import loader
from django.utils.safestring import mark_safe
from .models import SslConfig
import json


class SelectPKIWidget(Select):
    template_name = 'pki_select.html'

    def get_context(self, name, value, attrs=None):
        context = super(SelectPKIWidget, self).get_context(name, value, attrs)
        context['ssl_configs'] = json.dumps([x.to_ssl_config() for x in SslConfig.objects.all()])
        return context

    def render(self, name, value, attrs=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)
