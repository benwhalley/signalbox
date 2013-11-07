#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Admin classes for the Signalbox app'''
from django.contrib.auth import get_user_model
User = get_user_model()

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission
from reversion.admin import VersionAdmin
import selectable.forms as selectable
from django.core.exceptions import ValidationError
from signalbox.lookups import UserLookup
from signalbox.utilities.linkedinline import LinkedInline
from signalbox.models import *
from signalbox.allocation import *
from views import *
from django.conf import settings


# Only use VersionAdmin if site settings say so
ConditionalVersionAdmin = settings.USE_VERSIONING and VersionAdmin or admin.ModelAdmin


class ConditionInline(admin.StackedInline):
    model = StudyCondition
    extra = 0
    filter_horizontal = ['scripts']


class StudyPeriodInline(admin.TabularInline):
    model = StudyPeriod
    extra = 0


class StudyAdminForm(forms.ModelForm):

    def clean(self):
        problemscripts = filter(lambda x: x.asker is None, self.cleaned_data.get('ad_hoc_scripts', []))
        if problemscripts:
            raise ValidationError("All ad-hoc scripts must link to a Questionnaire ({})".format(
                ", ".join(map(lambda x: x.name, problemscripts)))
            )

        return self.cleaned_data


class StudyAdmin(admin.ModelAdmin):
    save_on_top = True
    list_filter = ['visible', 'paused', ]
    list_display = ['slug', 'visible', 'paused', 'visible_profile_fields', 'required_profile_fields']
    list_editable = ['visible', 'paused']
    filter_horizontal = [
        'ad_hoc_scripts',
        'createifs',
    ]
    prepopulated_fields = {'slug': ('name',)}
    form = StudyAdminForm
    fieldsets = (
        ("Main details", {

            'fields': (
                'name', 'slug', 'study_email',
                'visible', 'paused'
            )
        }),
        ('Study information fields', {
            'classes': ('collapse',),
            'fields': (
                'blurb',
                'study_image',
                'briefing',
                'consent_text',
                'welcome_text',)
        }),
        ('Capturing additional data', {
            'classes': ('collapse',),
            'fields': (
                'visible_profile_fields',
                'required_profile_fields',
                'ad_hoc_scripts',
                'createifs'
            )
        }),
        ('SMS and Telephone settings', {
            'classes': ('collapse',),
            'fields': (
                'twilio_number',
                'working_day_starts', 'working_day_ends'
            )
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': (
                'allocation_method',
                'auto_randomise',
                'auto_add_observations',
                'randomisation_probability',
                'show_study_condition_to_user'
            )
        }),
    )
    inlines = [ConditionInline, ]  # StudyPeriodInline

    def formfield_for_manytomany(self, db_field, request, **kwargs):
            if db_field.name == "administrators":
                kwargs["queryset"] = User.objects.filter(is_staff=True)
            return super(StudyAdmin, self).\
                formfield_for_manytomany(db_field, request, **kwargs)


class ObservationInline(LinkedInline):
    readonly_fields = [
        'n_in_sequence', 'script_type', 'ready_to_send', 'due',
        'due_original', 'last_attempted', 'attempt_count',
                        'n_questions_incomplete'
    ]
    exclude = ['offset', 'label']
    model = Observation
    extra = 0


class ReplyInline(LinkedInline):
    model = Reply
    max_num = 0
    readonly_fields = ['complete', 'last_submit', 'user', 'asker']
    fields = ['asker', 'is_canonical_reply', 'complete',
              'originally_collected_on', 'last_submit', 'user']


class ObservationDataInline(admin.StackedInline):
    save_on_top = True
    model = ObservationData
    readonly_fields = ['key', 'value', ]
    max_num = 0


class ReminderInstanceInline(LinkedInline):
    model = ReminderInstance
    readonly_fields = ['due', 'sent']
    max_num = 0
    exclude = ['reminder']


class ObservationAdmin(ConditionalVersionAdmin):
    save_on_top = True
    date_hierarchy = 'due'
    search_fields = ['token', 'dyad__study__slug', 'dyad__user__first_name',
                     'dyad__user__last_name', 'dyad__user__username']
    list_display = ["label", "token", "user", "due", "status",
                    "script_type", "n_questions", "n_questions_incomplete"]
    list_filter = ('due_original', 'status', 'attempt_count', 'dyad__study',
                   'dyad__user__userprofile__site', 'created_by_script__script_type', )
    list_display_links = ['label', 'token']
    ordering = ('due_original', )
    actions = ['resend_obs']
    readonly_fields = [
        'n_in_sequence', 'label', 'status', 'dyad',
        'token', 'last_attempted', 'due_original',
        'attempt_count', 'offset',
        'n_questions', 'n_questions_incomplete'
    ]
    inlines = [ReplyInline, ObservationDataInline, ReminderInstanceInline]

    def resend_obs(self, request, queryset):
        """Resend selected observations (calls their do() method)"""
        if not request.user.has_perm('signalbox.can_force_send'):
            return HttpResponseForbidden("You don't have permission")
        obs = [(o.do(), o) for o in queryset]
        messages.add_message(request, messages.INFO,
                             "Attempting to resend %s observations. ID#: %s" %
                             (len(obs), ", ".join([str(i[1].id) for i in obs])))
    resend_obs.short_description = "Resend these observations."


class MembershipAdminForm(forms.ModelForm):
    user = selectable.AutoCompleteSelectField(lookup_class=UserLookup)

    class Meta(object):
        model = Membership


class MembershipAdmin(admin.ModelAdmin):
    """Main Admin view for managing a user once they have joined the study.

    Condition and study fields are set to readonly to prevent accidentally
    reallocating or similar. A separate view is available to add participants.
    """

    form = MembershipAdminForm
    date_hierarchy = 'date_joined'
    save_on_top = True
    list_display = ('user', 'active', 'questions_answered', 'study',
                    'condition', 'date_randomised')
    list_filter = ('date_joined', 'study', 'user__userprofile__site',)
    search_fields = ('user__username', 'user__last_name', 'user__first_name',
                     'user__email',)
    ordering = ('user',)
    list_editable = ['active']
    readonly_fields = []  # ['date_randomised', ]
    fieldsets = (
        ("User", {
            'fields': ('user', 'active', 'relates_to', 'date_randomised', )
        }),

        ("Study and condition", {
            'fields': ('study', 'condition', )
        }),
    )

    inlines = [ObservationInline]
    save_on_top = True


# Define an inline admin descriptor for UserProfile model
# which acts a bit like a singleton
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    fk_name = 'user'
    can_delete = False
    max_num = 1
    extra = 0
    verbose_name_plural = 'profile'


# Define a new User admin
class UserAdmin(UserAdmin):
    save_on_top = True
    inlines = [UserProfileInline]


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class ScriptReminderInline(LinkedInline):
    model = ScriptReminder
    extra = 0


class ScriptAdmin(admin.ModelAdmin):
    save_on_top = True
    prepopulated_fields = {
        'reference': ('name',),
        'script_subject': ('name',),
    }
    list_display = ['admin_display_name', 'script_type',
                    'preview_of_datetimes']
    list_filter = ['script_type']
    search_fields = ['name']
    fieldsets = (
        ("General", {
            'fields': ('name', 'reference', 'script_type', )
        }),
        ("Study management", {
            'fields': (
                'asker',
                'external_asker_url',
                'is_clinical_data',
                'breaks_blind', 'allow_display_of_results',
                'show_in_tasklist', 'show_replies_on_dashboard',
            )
        }),


        ("Make observations at these times", {
         'fields': ('natural_date_syntax', )
         }
         ),

        ("Advanced Repetition", {
            'classes': ('collapse',),
            'fields': (
                'max_number_observations', 'repeat',
                'repeat_interval', 'repeat_byhours',
                'repeat_byminutes', 'repeat_bydays',
                'repeat_bymonths', 'repeat_bymonthdays'
            )
        }),

        ("Advanced Timing", {
            'classes': ('collapse',),
            'fields': (
                'repeat_from', 'delay_in_whole_days_only',
                'delay_by_minutes', 'delay_by_hours', 'delay_by_days',
                'completion_window', 'jitter',
            )
        }),

        ("Present to participants", {
            'fields':
            (
                'label',
                'script_subject', 'script_body',
                'user_instructions',
            )
        }),
    )
    inlines = [ScriptReminderInline]


class PermissionAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ['name', 'codename', 'content_type__name']


class StudyPeriodAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'study', 'show_dates']
    list_filter = ['study']


class ScoreSheetAdmin(admin.ModelAdmin):
    filter_horizontal = ['variables']


class StudyConditionAdmin(admin.ModelAdmin):
    list_display = ['tag', 'study']
    list_filter = ['study']
    filter_horizontal = ['scripts']


class UserMessageAdmin(admin.ModelAdmin):
    list_filter = ['state']
    list_display = ['message_to', 'message_from', 'state']
    readonly_fields = ['message_type', 'message_from', 'message_to', 'state',
                       'subject', 'message', 'last_modified']


class ContactRecordAdmin(admin.ModelAdmin):
    list_filter = ['reason', 'added']
    list_display = ['participant', 'added_by', 'added']
    readonly_fields = ['participant', 'added', 'added_by', 'reason', 'notes']


class AnswerAdmin(ConditionalVersionAdmin):
    date_hierarchy = 'last_modified'
    save_on_top = True
    readonly_fields = ['question', 'other_variable_name', 'reply',
                       'answer', 'choices', 'meta']
    search_fields = [
        'reply__token', 'reply__observation__dyad__user__username',
        'question__variable_name', 'reply__observation__token',
        'answer']

    list_display = ['question', 'answer', 'other_variable_name', 'study',
                    'participant', 'created', 'choices']
    list_filter = ['created', 'reply__observation__dyad__study']
    ordering = ['created', 'reply__observation__dyad']


class AnswerInline(LinkedInline):
    model = Answer
    fields = ['question', 'choices', 'answer']
    readonly_fields = ['question', 'choices', 'answer']
    extra = 0


class ReplyAdmin(ConditionalVersionAdmin):

    date_hierarchy = 'last_submit'
    save_on_top = True
    readonly_fields = ['complete', 'observation', 'user', 'asker',
                    'last_submit', 'started']
    list_display = ['token', 'entry_method', 'user', 'complete',
                    'last_submit', 'observation', 'collector']
    list_filter = ['asker', 'complete', 'observation__dyad__study', 'entry_method', 'collector']
    search_fields = ['token', 'observation__token']
    inlines = [AnswerInline, ]
    fieldsets = (
        ("Actions", {
            'fields': ('is_canonical_reply', )
        }),
        ("Status", {
            'fields': ('complete', 'last_submit')
        }),

        ("General", {
            'fields': ('observation', 'asker', 'started',
                       'entry_method', 'notes', 'redirect_to')
        }),

        ("External APIs", {
            'fields': ('external_id', 'twilio_question_index')
        }),)


class ObservationDataAdmin(admin.ModelAdmin):
    list_display = ['added', 'key', 'value', 'observation']
    list_filter = ['added', 'key']


class TextMessageCallbackAdmin(admin.ModelAdmin):
    list_display = ['sid', 'from_', 'message', 'status', 'timestamp',
                    'likely_related_user']
    readonly_fields = ['post', 'sid']
    list_filter = ['status', 'likely_related_user']


admin.site.register(TextMessageCallback, TextMessageCallbackAdmin)
admin.site.register(ObservationCreator)
admin.site.register(Reply, ReplyAdmin)
admin.site.register(Alert)
admin.site.register(AlertInstance)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(ScoreSheet, ScoreSheetAdmin)
admin.site.register(StudyPeriod, StudyPeriodAdmin)
admin.site.register(Observation, ObservationAdmin)
admin.site.register(ObservationData, ObservationDataAdmin)
admin.site.register(Membership, MembershipAdmin)
admin.site.register(Script, ScriptAdmin)
admin.site.register(Reminder,)
admin.site.register(Study, StudyAdmin)
admin.site.register(StudySite, )
admin.site.register(ScriptType, )
admin.site.register(ContactReason, )
admin.site.register(ContactRecord, ContactRecordAdmin)
admin.site.register(StudyCondition, StudyConditionAdmin)
admin.site.register(UserMessage, UserMessageAdmin)

admin.site.unregister(Permission, )
admin.site.register(Permission, PermissionAdmin)
