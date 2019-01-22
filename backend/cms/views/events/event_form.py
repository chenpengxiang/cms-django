from datetime import time, timedelta

from django import forms

from cms.models.event import EventTranslation, Event, RecurrenceRule


class EventForm(forms.ModelForm):
    # General event related fields
    picture = forms.ImageField(required=False)
    start_date = forms.DateField(input_formats=['%d.%m.%Y'], label='Beginn (Datum)')
    start_time = forms.TimeField(input_formats=['%H:%M'], label='Beginn (Uhrzeit)')
    end_date = forms.DateField(input_formats=['%d.%m.%Y'], label='Ende (Datum)')
    end_time = forms.TimeField(input_formats=['%H:%M'], label='Ende (Uhrzeit')
    frequency = forms.ChoiceField(choices=RecurrenceRule.FREQUENCY, label='Häufigkeit')
    interval = forms.IntegerField(min_value=1)
    weekdays_for_weekly = forms.MultipleChoiceField(choices=RecurrenceRule.WEEKDAYS,
                                                    widget=forms.CheckboxSelectMultiple)
    weekday_for_monthly = forms.ChoiceField(choices=RecurrenceRule.WEEKDAYS)
    week_for_monthly = forms.ChoiceField(
        choices=[(1, '1.'), (2, '2.'), (3, '3.'), (4, '4.'), (5, '5.')])
    recurrence_end_date = forms.DateField(input_formats=['%d.%m.%Y'], label='Wiederholungsenddatum')
    is_all_day = forms.BooleanField(label='Ganztägiges Event')
    is_recurring = forms.BooleanField(label='Wiederkehrendes Event')
    has_recurrence_end_date = forms.BooleanField(label='Wiederholung hat Enddatum')

    # Event translation related fields
    status = forms.ChoiceField(choices=EventTranslation.STATUS)
    minor_edit = forms.BooleanField()
    public = forms.BooleanField()

    class Meta:
        model = EventTranslation
        fields = ['title', 'description', 'status', 'language']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(EventForm, self).__init__(*args, **kwargs)
        # TODO: get available languages from site settings
        self.fields['language'] = forms.ChoiceField(
            choices=[('de', 'Deutsch'),
                     ('ar', 'Arabisch'),
                     ('fa', 'Farsi'),
                     ('fr', 'Französisch'),
                     ('tr', 'Türkisch')])

    def save(self, commit=True, event_translation_id=None):
        # TODO: version, active_version

        # Maybe move code for setting the values to this function...
        # but not sure about behavior regarding call-by-object
        # def set_data(self, event):

        if event_translation_id:
            p = EventTranslation.objects.filter(
                id=event_translation_id).select_related('event').first()

            # save event
            event = Event.objects.get(id=p.event.id)
            event.picture = self.cleaned_data['picture']
            event.start_date = self.cleaned_data['start_date']
            event.location = self.cleaned_data['location']
            if self.cleaned_data['is_all_day']:
                event.start_time = time(0, 0, 0, 0)
                event.end_date = event.start_date + timedelta(days=1)
                event.end_time = time(0, 0, 0, 0)
            else:
                event.start_time = self.cleaned_data['start_time']
                event.end_date = self.cleaned_data['end_date']
                event.end_time = self.cleaned_data['end_time']
            if self.cleaned_data['is_recurring']:
                event.recurrence_rule.frequency = self.cleaned_data['frequency']
                event.recurrence_rule.interval = self.cleaned_data['interval']
                event.recurrence_rule.weekdays_for_weekly = self.cleaned_data['weekdays_for_weekly']
                event.recurrence_rule.weekday_for_monthly = self.cleaned_data['weekday_for_monthly']
                event.recurrence_rule.week_for_monthly = self.cleaned_data['week_for_monthly']
                if self.cleaned_data['has_recurrence_end_date']:
                    event.recurrence_rule.end_date = self.cleaned_data['recurrence_end_date']
            event.save()

            # save event translation
            event_translation = EventTranslation.objects.get(id=p.id)
            event_translation.title = self.cleaned_data['title']
            event_translation.description = self.cleaned_data['description']
            event_translation.status = self.cleaned_data['status']
            event_translation.language = self.cleaned_data['language']
            event_translation.minor_edit = self.cleaned_data['minor_edit']
            event_translation.public = self.cleaned_data['public']
            event_translation.save()
        else:
            # create event
            event = Event.objects.create(
                picture=self.cleaned_data['picture'],
                start_date=self.cleaned_data['start_date'],
                location=self.cleaned_data['location']
            )

            if self.cleaned_data['is_all_day']:
                event.start_time = time(0, 0, 0, 0)
                event.end_date = event.start_date + timedelta(days=1)
                event.end_time = time(0, 0, 0, 0)
            else:
                event.start_time = self.cleaned_data['start_time']
                event.end_date = self.cleaned_data['end_date']
                event.end_time = self.cleaned_data['end_time']
            if self.cleaned_data['is_recurring']:
                event.recurrence_rule.frequency = self.cleaned_data['frequency']
                event.recurrence_rule.interval = self.cleaned_data['interval']
                event.recurrence_rule.weekdays_for_weekly = self.cleaned_data['weekdays_for_weekly']
                event.recurrence_rule.weekday_for_monthly = self.cleaned_data['weekday_for_monthly']
                event.recurrence_rule.week_for_monthly = self.cleaned_data['week_for_monthly']
                if self.cleaned_data['has_recurrence_end_date']:
                    event.recurrence_rule.end_date = self.cleaned_date['recurrence_end_date']
            event.save()

            # create event translation
            event_translation = EventTranslation.objects.create(
                title=self.cleaned_data['title'],
                description=self.cleaned_data['description'],
                status=self.cleaned_data['status'],
                language=self.cleaned_data['language'],
                minor_edit=self.cleaned_data['minor_edit'],
                public=self.cleaned_data['public'],
                event=event,
                creator=self.user
            )
