from django.contrib import admin
from django.utils import timezone
from django import forms

from .models import QuestionOption
from .models import Question
from .models import Voting
from census.models import CensusGroup

from .filters import StartedFilter


def start(modeladmin, request, queryset):
    for v in queryset.all():
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()


def stop(ModelAdmin, request, queryset):
    for v in queryset.all():
        v.end_date = timezone.now()
        v.save()


def tally(ModelAdmin, request, queryset):
    for v in queryset.filter(end_date__lt=timezone.now()):
        token = request.session.get('auth-token', '')
        v.tally_votes(token)


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption


class QuestionAdmin(admin.ModelAdmin):
    inlines = [QuestionOptionInline]


class VotingAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    readonly_fields = ('start_date', 'end_date', 'pub_key',
                       'tally', 'postproc')
    date_hierarchy = 'start_date'
    list_filter = (StartedFilter,)
    search_fields = ('name', )

    actions = [start, stop, tally]


class VotingAdminForm(forms.ModelForm):
    group = forms.ModelChoiceField(queryset=CensusGroup.objects.all(), required=False, label='Select Group')

    class Meta:
        model = Voting
        fields = '__all__'


admin.site.register(Voting, VotingAdmin)
admin.site.register(Question, QuestionAdmin)
