"""
Form for creating an organization object
"""

from django import forms
from ...models.organization import Organization


class OrganizationForm(forms.ModelForm):
    """
    DjangoForm Class, that can be rendered to create deliverable HTML

    Args:
        forms : Defines the form as an Model form related to a database object
    """

    class Meta:
        model = Organization
        fields = ['name', 'slug', 'thumbnail',]

    def __init__(self, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)

    def save_organization(self, organization_id=None):
        """Function to create or update an organization
            organization_id ([Integer], optional): Defaults to None. If it's not set creates
            a organization or update the organization with the given region slug.
        """

        if organization_id:
            # save organization
            organization = Organization.objects.get(id=organization_id)
            organization.name = self.cleaned_data['name']
            organization.slug = self.cleaned_data['slug']
            organization.thumbnail = self.cleaned_data['thumbnail']
            organization.save()
        else:
            # create region
            organization = Organization.objects.create(
                name=self.cleaned_data['name'],
                slug=self.cleaned_data['slug'],
                thumbnail=self.cleaned_data['thumbnail']
            )

        return organization
