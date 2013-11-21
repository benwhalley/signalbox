"""Admin setup for Questionnaire app"""

from datetime import datetime
from django.contrib import admin
from django.contrib.auth.models import Permission
from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages

from ask.models import AskPage, QuestionAsset, Instrument, Choice, ShowIf, Asker, Question, ChoiceSet
import ask.models.fields

from signalbox.utilities.linkedinline import LinkedInline
from ask.lookups import QuestionLookup
import selectable.forms as selectable
from django.forms import widgets
from django.db import models


class ShowIfForm(forms.ModelForm):
    previous_question = selectable.AutoCompleteSelectField(lookup_class=QuestionLookup,
        required=False)

    class Meta(object):
        model = ShowIf


class ShowIfAdmin(admin.ModelAdmin):
    form = ShowIfForm
    save_on_top = True


class QuestionInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestionInlineForm, self).__init__(*args, **kwargs)
        # self.fields['order'].widget = forms.TextInput(attrs={'class':'hidden_order_field'})
        self.fields['text'].widget = widget=forms.Textarea(attrs={'rows':'2', 'class':'question_text_field'})
        self.fields['variable_name'].widget = widget=forms.TextInput(attrs={'class': 'variable_name_field', 'maxlength':32})


class QuestionInlineForPage(admin.StackedInline):
    template = "admin/ask/question/inline.html"
    fk_name = 'page'
    form = QuestionInlineForm
    model = Question
    order_by = ['order']
    readonly_fields = ['page', 'instrument']
    prepopulated_fields = {
        'variable_name': ('text',),
    }

    fieldsets = (
            ("Question text", {
                'fields': (
                    'text',
                    'variable_name',
                    'q_type',
                    'choiceset',
                    )
            }),

            ("Options", {
                'fields': (
                    'order',
                    'required',
                    'display_instrument',
                    'showif',
                    'help_text',
                    'allow_not_applicable',
                    'audio',
                    'score_mapping',
                    'widget_kwargs'
                    )
            }),
        )

    extra = 1
    admin_model_path = "question"


class QuestionInlineForInstrument(QuestionInlineForPage):
    fk_name = 'instrument'


class AskPageAdmin(admin.ModelAdmin):
    save_on_top = True
    readonly_fields = ['asker', 'page_number']
    exclude = ['order']
    list_filter = ['asker']
    inlines = [QuestionInlineForPage]

    def response_change(self, request, obj):
        """Return to the Questionnaire after saving."""

        if request.POST.get("_continue", None):
            return HttpResponseRedirect("")  # redirect back to current page
        else:
            return HttpResponseRedirect(reverse("admin:ask_asker_change",
                args=(str(obj.asker.id), )))


class AskPageInline(LinkedInline):
    model = AskPage
    ordering = ['order']
    extra = 0


class AskerAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AskerAdminForm, self).__init__(*args, **kwargs)
        self.fields['success_message'].widget = widget=forms.Textarea(attrs={'rows':'2'})


class AskerAdmin(admin.ModelAdmin):
    save_on_top = True
    form = AskerAdminForm
    search_fields = ['name', 'slug', ]
    list_display = ['slug', 'name', ]
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['name', ]
    inlines = [AskPageInline]
    def purge_preview_replies(self, request, queryset):
        """Purge preview replies for this asker."""
        previews = [i.reply_set.filter(entry_method="preview") for i in queryset]
        reps = sum([i.count() for i in previews])
        [i.delete() for i in previews]
        messages.add_message(request, messages.INFO, "Deleted %s preview reply." % reps, )
    purge_preview_replies.short_description = "Delete preview replies and answers."

    actions = [purge_preview_replies]
    fieldsets = (
        ("Main details", {
            'fields': (
                'name',
                'slug',
                )
        }),
        ("Settings", {
            'fields': (
                'success_message',
                'redirect_url',
                'steps_are_sequential',
                'step_navigation',
                'show_progress',
                'hide_menu',
                ),
            # 'classes': ('collapse',),
        }),
    )



class InstrumentAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ['name', 'citation']
    inlines = [QuestionInlineForInstrument]

    class Media:
        js = ("js/questions.js",)


class ChoiceInline(admin.TabularInline):
    model = Choice
    ordering = ['order']
    extra = 3


class ChoiceSetAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ['name', 'choice__label']
    # inlines = [ChoiceInline]
    list_display = ['name', 'choices_as_string']


class QuestionAdminForm(forms.ModelForm):

    class Meta:
        widgets = {
            'text': forms.Textarea(attrs={'cols': 80, 'rows': 10}),
            # 'variable_label': forms.Textarea(attrs={'cols': 80, 'rows': 3}),
            'help_text': forms.Textarea(attrs={'cols': 80, 'rows': 3}),
        }


class QuestionAssetInline(admin.TabularInline):
    model = QuestionAsset
    ordering = ['slug']
    extra = 1


class QuestionAdmin(admin.ModelAdmin):
    form = QuestionAdminForm
    save_on_top = True
    save_as = True
    search_fields = ['text', 'variable_name']
    list_display = ['variable_name', 'text', 'q_type']
    inlines = [QuestionAssetInline]

    fieldsets = (
        ("Question data", {
        'fields': ( 'order', 'q_type', 'choiceset', 'scoresheet', 'text', 'variable_name', 'required',  'score_mapping')
        }),

        ("Additional info", {
        'fields': ( 'help_text', 'audio')
        }),

        ("Advanced", {
        'classes': ('collapse',),
        'fields': (
            'field_kwargs', 'widget_kwargs'
        )
        }
    ))


admin.site.register(Permission,)
admin.site.register(ShowIf, ShowIfAdmin)
admin.site.register(Asker, AskerAdmin)
admin.site.register(AskPage, AskPageAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Instrument, InstrumentAdmin)
admin.site.register(ChoiceSet, ChoiceSetAdmin)
