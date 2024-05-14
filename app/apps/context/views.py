from apps.context.forms import ContextAanmakenForm, ContextAanpassenForm
from apps.context.models import Context
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.context_bekijken", raise_exception=True),
    name="dispatch",
)
class ContextView(View):
    model = Context
    success_url = reverse_lazy("context_lijst")


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.context_lijst_bekijken", raise_exception=True),
    name="dispatch",
)
class ContextLijstView(ContextView, ListView):
    ...


class ContextAanmakenAanpassenView(ContextView):
    def form_valid(self, form):
        form.instance.filters = {"fields": form.cleaned_data.get("filters")}
        return super().form_valid(form)


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.context_aanpassen", raise_exception=True),
    name="dispatch",
)
class ContextAanpassenView(ContextAanmakenAanpassenView, UpdateView):
    form_class = ContextAanpassenForm

    def get_initial(self):
        initial = self.initial.copy()
        obj = self.get_object()
        initial["filters"] = obj.filters.get("fields", [])
        return initial


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.context_aanmaken", raise_exception=True),
    name="dispatch",
)
class ContextAanmakenView(ContextAanmakenAanpassenView, CreateView):
    form_class = ContextAanmakenForm


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.context_verwijderen", raise_exception=True),
    name="dispatch",
)
class ContextVerwijderenView(ContextView, DeleteView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
