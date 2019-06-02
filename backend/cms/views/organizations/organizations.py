from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView
from django.shortcuts import render

from .organization_form import OrganizationForm
from ...models.organization import Organization
from ...decorators import staff_required


@method_decorator(login_required, name='dispatch')
@method_decorator(staff_required, name='dispatch')
class OrganizationListView(PermissionRequiredMixin, TemplateView):
    permission_required = 'cms.view_organization'
    raise_exception = True

    template_name = 'organizations/list.html'
    base_context = {'current_menu_item': 'organizations'}

    def get(self, request, *args, **kwargs):
        organizations = Organization.objects.all()

        return render(
            request,
            self.template_name,
            {
                **self.base_context,
                'organizations': organizations
            }
        )


@method_decorator(login_required, name='dispatch')
@method_decorator(staff_required, name='dispatch')
class OrganizationView(PermissionRequiredMixin, TemplateView):
    permission_required = 'cms.view_organization'
    raise_exception = True

    template_name = 'organizations/organization.html'
    base_context = {'current_menu_item': 'organizations'}

    def get(self, request, *args, **kwargs):
        organization_id = self.kwargs.get('organization_id', None)
        if organization_id:
            if not request.user.has_perm('cms.change_organization'):
                raise PermissionDenied
            organization = Organization.objects.get(id=organization_id)
            form = OrganizationForm(instance=organization)
        else:
            if not request.user.has_perm('cms.add_organization'):
                raise PermissionDenied
            form = OrganizationForm()
        return render(request, self.template_name, {
            'form': form,
            **self.base_context
        })

    def post(self, request, organization_id=None):
        # TODO: error handling
        if organization_id:
            if not request.user.has_perm('cms.change_organization'):
                raise PermissionDenied
            organization = Organization.objects.get(id=organization_id)
            form = OrganizationForm(request.POST, instance=organization)
            success_message = _('Organization created successfully')
        else:
            if not request.user.has_perm('cms.add_organization'):
                raise PermissionDenied
            form = OrganizationForm(request.POST)
            success_message = _('Organization saved successfully')

        if form.is_valid():
            form.save()
            messages.success(request, success_message)
            # TODO: improve messages
        else:
            messages.error(request, _('Errors have occurred.'))

        return render(request, self.template_name, {
            'form': form,
            **self.base_context
        })
