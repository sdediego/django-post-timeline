from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

# Define your app configuration here.

class TimelineConfig(AppConfig):
    name = 'timeline'
    verbose_name = _('Timeline')
    label = 'timeline'


    def ready(self):
        # Import your signal functions here.
        import .signals
