from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class OnlinejudgeConfig(AppConfig):
    name = 'onlinejudge'
    verbose_name = _("Django Online Judge")
