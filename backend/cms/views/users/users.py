from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView
from django.shortcuts import render
from ...models.user import User
from .user_form import BaseUserForm, UserForm


@method_decorator(login_required, name='dispatch')
class UserListView(TemplateView):
    template_name = 'users/list.html'
    base_context = {'current_menu_item': 'users'}

    def get(self, request, *args, **kwargs):
        users = User.objects.all()

        return render(
            request,
            self.template_name,
            {
                **self.base_context,
                'users': users
            }
        )

@method_decorator(login_required, name='dispatch')
class UserView(TemplateView):
    template_name = 'users/user.html'
    base_context = {'current_menu_item': 'users'}

    def get(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id', None)
        if user_id:
            base_user = get_user_model().objects.get(id=user_id)
            user = User.objects.get(user=base_user)
            base_user_form = BaseUserForm(initial=base_user.__dict__)
            user_form = UserForm(initial=user.__dict__)
        else:
            base_user_form = BaseUserForm()
            user_form = UserForm()
        return render(request, self.template_name, {
            'base_user_form': base_user_form,
            'user_form': user_form,
            **self.base_context
        })

    def post(self, request, user_id=None):
        # TODO: error handling
        base_user_form = BaseUserForm(request.POST)
        user_form = UserForm(request.POST)
        if base_user_form.is_valid() and user_form.is_valid():
            if user_id:
                base_user = base_user_form.save_user(user_id=user_id)
                user_form.save_user(base_user_id=base_user.id)
                messages.success(request, _('User saved successfully.'))
            else:
                base_user = base_user_form.save_user()
                user_form.save_user(base_user_id=base_user.id)
                messages.success(request, _('User created successfully'))
            # TODO: improve messages
        else:
            messages.error(request, _('Errors have occurred.'))

        return render(request, self.template_name, {
            'base_user_form': base_user_form,
            'user_form': user_form,
            **self.base_context
        })
