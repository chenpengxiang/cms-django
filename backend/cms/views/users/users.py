from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView
from django.shortcuts import render

from .user_form import UserForm, UserProfileForm
from ...models.user_profile import UserProfile
from ...decorators import staff_required


@method_decorator(login_required, name='dispatch')
@method_decorator(staff_required, name='dispatch')
class UserListView(TemplateView):
    template_name = 'users/list.html'
    base_context = {'current_menu_item': 'users'}

    def get(self, request, *args, **kwargs):
        users = get_user_model().objects.all()

        return render(
            request,
            self.template_name,
            {
                **self.base_context,
                'users': users
            }
        )

@method_decorator(login_required, name='dispatch')
@method_decorator(staff_required, name='dispatch')
class UserView(TemplateView):
    template_name = 'users/user.html'
    base_context = {'current_menu_item': 'users'}

    def get(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id', None)
        if user_id:
            user = get_user_model().objects.get(id=user_id)
            user_form = UserForm(instance=user)
            user_profile = UserProfile.objects.filter(user=user)
            if user_profile.exists():
                user_profile_form = UserProfileForm(instance=user_profile.first())
            else:
                user_profile_form = UserProfileForm()
        else:
            user_form = UserForm()
            user_profile_form = UserProfileForm()
        return render(request, self.template_name, {
            'user_form': user_form,
            'user_profile_form': user_profile_form,
            **self.base_context
        })

    def post(self, request, user_id=None):
        # TODO: error handling

        user = get_user_model().objects.filter(id=user_id).first()
        if user:
            user_form = UserForm(request.POST, instance=user)
            success_message = _('User saved successfully.')
        else:
            user_form = UserForm(request.POST)
            success_message = _('User created successfully.')

        user_profile = UserProfile.objects.filter(user=user).first()
        if user_profile:
            user_profile_form = UserProfileForm(request.POST, instance=user_profile)
        else:
            user_profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and user_profile_form.is_valid():
            user = user_form.save()
            if user_profile:
                user_profile_form.save()
            else:
                user_profile = user_profile_form.save(commit=False)
                user_profile.user = user
                user_profile.save()
            messages.success(request, success_message)
        else:
            # TODO: improve messages
            messages.error(request, _('Errors have occurred.'))

        return render(request, self.template_name, {
            'user_form': user_form,
            'user_profile_form': user_profile_form,
            **self.base_context
        })
