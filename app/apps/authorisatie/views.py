from apps.authorisatie.forms import RechtengroepAanmakenForm, RechtengroepAanpassenForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.rechtengroep_bekijken", raise_exception=True),
    name="dispatch",
)
class RechtengroepView(View):
    model = Group
    success_url = reverse_lazy("rechtengroep_lijst")


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required(
        "authorisatie.rechtengroep_lijst_bekijken", raise_exception=True
    ),
    name="dispatch",
)
class RechtengroepLijstView(RechtengroepView, ListView):
    ...


class RechtengroepAanmakenAanpassenView(RechtengroepView):
    ...


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.rechtengroep_aanpassen", raise_exception=True),
    name="dispatch",
)
class RechtengroepAanpassenView(RechtengroepAanmakenAanpassenView, UpdateView):
    form_class = RechtengroepAanpassenForm


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.rechtengroep_aanmaken", raise_exception=True),
    name="dispatch",
)
class RechtengroepAanmakenView(RechtengroepAanmakenAanpassenView, CreateView):
    form_class = RechtengroepAanmakenForm


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.rechtengroep_verwijderen", raise_exception=True),
    name="dispatch",
)
class RechtengroepVerwijderenView(RechtengroepView, DeleteView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
