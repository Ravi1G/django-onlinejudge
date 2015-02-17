#@PydevCodeAnalysisIgnore
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import patterns, url

urlpatterns = patterns('onlinejudge.views',
    url(_(r"^$"),                                               "index",                         {}, "index"),
    url(_(r"^challenge/(?P<slug>[-\w]+)/$"),                    "challenge",                     {}, "challenge"),
    url(_(r"^challenge/(?P<slug>[-\w]+)/update/$"),             "challenge_update",              {}, "challenge_update"),
    url(_(r"^challenge/(?P<slug>[-\w]+)/report/$"),             "challenge_report",              {}, "challenge_report"),
    url(_(r"^contest/(?P<slug>[-\w]+)/report/$"),               "contest_report",                {}, "contest_report"),
    url(_(r"^submission/(?P<id>[\d]+)/grade/$"),                "grade_submission",              {}, "grade_submission"),
    # ajax
    url(_(r"^challenge/(?P<slug>[-\w]+)/template/$"),           "challenge_submission_template", {}, "challenge_submission_template"),
    url(_(r"^challenge/(?P<slug>[-\w]+)/submission/test/$"),    "submission_test",               {}, "submission_test"),
    url(_(r"^challenge/(?P<slug>[-\w]+)/submission/results/$"), "submission_results",            {}, "submission_results"),
)
