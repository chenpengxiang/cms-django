"""
Form for creating a page object and page translation object
"""

import sys
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db.models import Q
from django.utils.text import slugify
from django.utils.translation import ugettext as _

from guardian.utils import get_anonymous_user
from guardian.shortcuts import assign_perm, remove_perm, get_users_with_perms

from ...models import Page, PageTranslation, Site, Language
from ..general import POSITION_CHOICES


class PageForm(forms.ModelForm):
    """
    DjangoForm Class, that can be rendered to create deliverable HTML

    Args:
        forms : Defines the form as an Model form related to a database object
    """

    position = forms.ChoiceField(choices=POSITION_CHOICES)
    parent = forms.ModelChoiceField(queryset=Page.objects.all(), required=False)
    icon = forms.ImageField(required=False)
    PUBLIC_CHOICES = (
        (True, _('Public')),
        (False, _('Private'))
    )
    public = forms.ChoiceField(choices=PUBLIC_CHOICES)
    permission_change_page = Permission.objects.get(codename='change_page')
    users_without_permission = get_user_model().objects.exclude(
        Q(groups__permissions=permission_change_page) |
        Q(user_permissions=permission_change_page) |
        Q(is_superuser=True) |
        Q(id=get_anonymous_user().id)
    )
    editors = forms.ModelMultipleChoiceField(queryset=users_without_permission, required=False)

    class Meta:
        model = PageTranslation
        fields = ['title', 'text', 'status']


    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PageForm, self).__init__(*args, **kwargs)

    def save_page(self, site_slug, language_code, page_id=None, publish=False, archived=False):
        """Function to create or update a page

            page_id ([Integer], optional): Defaults to None.
            publish ([Boolean], optional): Defaults to False. Flag for changing publication status
                                           via publish button.

            Returns:
                page: the created or updated page
        """

        slug = slugify(self.cleaned_data['title'])
        page_translation = PageTranslation.objects.filter(
            page__id=page_id,
            language__code=language_code
        ).first()
        # make sure the slug derived from the title is unique
        if (
                (
                    (
                        # page is created
                        not page_id
                        or
                        # translation is created
                        not page_translation
                    )
                    or
                    # slug has changed
                    page_translation.slug != slug
                )
                and
                # the new slug already exists
                PageTranslation.objects.filter(slug=slug).exists()
        ):
            old_slug = slug
            i = 1
            while True:
                i += 1
                slug = old_slug + '-' + str(i)
                if not PageTranslation.objects.filter(slug=slug).exists():
                    break

        # TODO: version, active_version

        if publish:
            self.cleaned_data['public'] = True

        # TODO: version, active_version
        if page_id:
            # save page
            page = Page.objects.get(id=page_id)
            page.icon = self.cleaned_data['icon']
            if archived:
                page.public = False
                page.archived = True
            else:
                page.public = self.cleaned_data['public']
            page.save()
            page.move_to(self.cleaned_data['parent'], self.cleaned_data['position'])
        else:
            # create page
            page = Page.objects.create(
                icon=self.cleaned_data['icon'],
                site=Site.objects.get(slug=site_slug),
            )
            page.move_to(self.cleaned_data['parent'], self.cleaned_data['position'])

        if page_translation:
            # save page translation
            page_translation.slug = slug
            page_translation.title = self.cleaned_data['title']
            page_translation.text = self.cleaned_data['text']
            page_translation.status = self.cleaned_data['status']
            page_translation.save()
        else:
            # create page translation
            page_translation = PageTranslation.objects.create(
                slug=slug,
                title=self.cleaned_data['title'],
                text=self.cleaned_data['text'],
                status=self.cleaned_data['status'],
                language=Language.objects.get(code=language_code),
                public=self.cleaned_data['public'],
                page=page,
                creator=self.user
            )

        old_editors = {user for user, perms in get_users_with_perms(page, attach_perms=True).items() if 'change_page' in perms}
        new_editors = set(self.cleaned_data['editors'])
        added_editors = new_editors - old_editors
        removed_editors = old_editors - new_editors
        for editor in added_editors:
            assign_perm('change_page', editor, page)
        for editor in removed_editors:
            remove_perm('change_page', editor, page)

        return page
