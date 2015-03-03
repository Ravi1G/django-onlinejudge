from __future__ import absolute_import
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.contrib.admin.options import TabularInline
from django.contrib.auth.models import User
from django.forms import ModelForm
from django_select2.fields import ModelSelect2MultipleField
from django.utils.encoding import smart_unicode
from .models import Challenge, Contest, Submission, TestCase
#REMOVE THIS
from .models import Challenge, Contest, Submission, TestCase, TestResult


class TestCaseInline(TabularInline):
    model = TestCase
    extra = 0


class ChallengeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'contest')
    list_filter = ('contest', )
    inlines = (TestCaseInline,)


class UserFullnameChoiceField(ModelSelect2MultipleField):
    def label_from_instance(self, obj):
        return smart_unicode(obj.get_full_name())


class ContestForm(ModelForm):
    participants = UserFullnameChoiceField(queryset=User.objects,
                                           required=True)

    class Meta:
        model = Contest


class ContestAdmin(admin.ModelAdmin):
    form = ContestForm
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'is_active', )

    class Media:
        js = (
            'onlinejudge/js/init-jquery.js',  # app static folder
        )


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('challenge', 'get_author', 'status',
                    'test_results_summary', 'modified', 'created',
                    'get_contest')
    list_filter = ('challenge__contest', 'challenge')
    readonly_fields = ['modified', 'created']

    def get_author(self, obj):
        return obj.author.get_full_name()
    get_author.short_description = _('Author')
    get_author.admin_order_field = 'author'

    def get_contest(self, obj):
        return obj.challenge.contest
    get_contest.short_description = _('Contest')
    get_contest.admin_order_field = 'challenge__contest'


class TestCaseAdmin(admin.ModelAdmin):
    exclude = ('disk_limit',)
    list_display = ('challenge', 'hint_short', 'is_public', 'input',
                    'output', 'cpu_time_limit',
                    'wallclock_time_limit', 'memory_limit')
#remove this
admin.site.register(TestResult)

admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(Contest, ContestAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(TestCase, TestCaseAdmin)
