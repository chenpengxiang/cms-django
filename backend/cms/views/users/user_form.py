"""
Form for creating a user object
"""

from django import forms
from django.contrib.auth import get_user_model
from ...models.user import User


class BaseUserForm(forms.ModelForm):
    """
    DjangoForm Class, that can be rendered to create deliverable HTML

    Args:
        forms : Defines the form as an Model form related to a database object
    """

    class Meta:
        model = get_user_model()
        fields = ['username', 'first_name', 'last_name', 'email',
                  'password', 'is_staff', 'is_active', 'is_superuser']

    def __init__(self, *args, **kwargs):
        super(BaseUserForm, self).__init__(*args, **kwargs)

    def save_user(self, user_id=None):
        """Function to create or update a user
            region_slug ([Integer], optional): Defaults to None. If it's not set creates
            a region or update the region with the given region slug.
        """

        if user_id:
            # save user
            user = get_user_model().objects.get(id=user_id)
            user.username = self.cleaned_data['username']
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.password = self.cleaned_data['password']
            user.is_staff = self.cleaned_data['is_staff']
            user.is_active = self.cleaned_data['is_active']
            user.is_superuser = self.cleaned_data['is_superuser']
            user.save()
        else:
            # create region
            user = get_user_model().objects.create(
                username=self.cleaned_data['username'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                email=self.cleaned_data['email'],
                password=self.cleaned_data['password'],
                is_staff=self.cleaned_data['is_staff'],
                is_active=self.cleaned_data['is_active'],
                is_superuser=self.cleaned_data['is_superuser'],
            )

        return user


class UserForm(forms.ModelForm):
    """
    DjangoForm Class, that can be rendered to create deliverable HTML

    Args:
        forms : Defines the form as an Model form related to a database object
    """

    class Meta:
        model = User
        fields = ['regions', 'organization']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

    def save_user(self, base_user_id=None):
        """Function to create or update a region
            region_slug ([Integer], optional): Defaults to None. If it's not set creates
            a region or update the region with the given region slug.
        """

        base_user = get_user_model().objects.get(id=base_user_id)
        user = User.objects.filter(user=base_user)

        if user.exists():
            # save user
            user = user.first()
            user.regions = self.cleaned_data['regions']
            user.organization = self.cleaned_data['organization']
            user.save()
        else:
            # create user
            user = User.objects.create(
                user=base_user,
                organization=self.cleaned_data['organization']
            )
            user.regions = self.cleaned_data['regions']
            user.save()

        return user
