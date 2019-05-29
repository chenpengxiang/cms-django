"""
Form for creating a user object
"""

from django import forms
from django.contrib.auth import get_user_model
from ...models.user_profile import UserProfile


class UserForm(forms.ModelForm):
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
        super(UserForm, self).__init__(*args, **kwargs)

class UserProfileForm(forms.ModelForm):
    """
    DjangoForm Class, that can be rendered to create deliverable HTML

    Args:
        forms : Defines the form as an Model form related to a database object
    """

    class Meta:
        model = UserProfile
        fields = ['regions', 'organization']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
