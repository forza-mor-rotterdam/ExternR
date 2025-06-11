import logging

from apps.authenticatie.forms import (
    GebruikerAanmakenForm,
    GebruikerAanpassenForm,
    GebruikerProfielForm,
)
from apps.instellingen.models import Instelling
from apps.meldingen.service import MeldingenService
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

Gebruiker = get_user_model()
logger = logging.getLogger(__name__)


class LoginView(View):
    def get(self, request, *args, **kwargs):
        if request.user.has_perms(["authorisatie.beheer_bekijken"]):
            return redirect(reverse("beheer"))
        if request.user.is_authenticated:
            return redirect(reverse("root"), False)

        if settings.OIDC_ENABLED:
            return redirect(f"/oidc/authenticate/?next={request.GET.get('next', '/')}")
        if settings.ENABLE_DJANGO_ADMIN_LOGIN:
            return redirect(f"/admin/login/?next={request.GET.get('next', '/admin')}")

        return HttpResponse("Er is geen login ingesteld")


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("login"), False)

        if settings.OIDC_ENABLED:
            return redirect("/oidc/logout/")
        if settings.ENABLE_DJANGO_ADMIN_LOGIN:
            return redirect(f"/admin/logout/?next={request.GET.get('next', '/')}")

        return HttpResponse("Er is geen logout ingesteld")


class GebruikerView(View):
    model = Gebruiker
    success_url = reverse_lazy("gebruiker_lijst")


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.gebruiker_lijst_bekijken", raise_exception=True),
    name="dispatch",
)
class GebruikerLijstView(GebruikerView, ListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object_list = self.object_list.select_related(
            "profiel__context"
        ).prefetch_related("groups")
        context["geauthoriseerde_gebruikers"] = object_list.filter(
            groups__isnull=False,
            verwijderd_op__isnull=True,
        )
        context["ongeauthoriseerde_gebruikers"] = object_list.filter(
            groups__isnull=True,
            verwijderd_op__isnull=True,
        )
        context["verwijderde_gebruikers"] = object_list.filter(
            verwijderd_op__isnull=False
        )
        return context


class GebruikerAanmakenAanpassenView(GebruikerView):
    def form_valid(self, form):
        if not hasattr(form.instance, "profiel"):
            form.instance.save()
        if form.cleaned_data.get("context"):
            form.instance.profiel.context = form.cleaned_data.get("context")
        else:
            form.instance.profiel.context = None
        form.instance.profiel.save()
        form.instance.groups.clear()
        if form.cleaned_data.get("group"):
            form.instance.groups.add(form.cleaned_data.get("group"))

        return super().form_valid(form)


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.gebruiker_aanpassen", raise_exception=True),
    name="dispatch",
)
class GebruikerAanpassenView(GebruikerAanmakenAanpassenView, UpdateView):
    form_class = GebruikerAanpassenForm
    template_name = "authenticatie/gebruiker_aanpassen.html"

    def get_initial(self):
        initial = self.initial.copy()
        obj = self.get_object()
        context = obj.profiel.context if hasattr(obj, "profiel") else None
        initial["context"] = context
        initial["group"] = obj.groups.all().first()
        return initial


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.gebruiker_aanmaken", raise_exception=True),
    name="dispatch",
)
class GebruikerAanmakenView(GebruikerAanmakenAanpassenView, CreateView):
    template_name = "authenticatie/gebruiker_aanmaken.html"
    form_class = GebruikerAanmakenForm


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.gebruiker_verwijderen", raise_exception=True),
    name="dispatch",
)
class GebruikerVerwijderenView(GebruikerAanmakenAanpassenView, UpdateView):
    def get(self, request, *args, **kwargs):
        object = self.get_object()
        object.verwijderd_op = timezone.now()
        object.groups.clear()
        object.save(update_fields=["verwijderd_op"])
        messages.success(
            request,
            f"De gebruiker '{object.email}' is verwijderd",
        )
        return redirect(reverse("gebruiker_lijst"))


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.gebruiker_terughalen", raise_exception=True),
    name="dispatch",
)
class GebruikerTerughalenView(GebruikerAanmakenAanpassenView, UpdateView):
    def get(self, request, *args, **kwargs):
        object = self.get_object()
        object.verwijderd_op = None
        object.save(update_fields=["verwijderd_op"])
        messages.success(
            request,
            f"De gebruiker '{object.email}' is teruggehaald",
        )
        return redirect(reverse("gebruiker_lijst"))


@method_decorator(login_required, name="dispatch")
class GebruikerProfielView(UpdateView):
    model = Gebruiker
    form_class = GebruikerProfielForm
    template_name = "authenticatie/gebruiker_profiel.html"
    success_url = reverse_lazy("gebruiker_profiel")

    def get_context_data(self, **kwargs):
        instelling = Instelling.actieve_instelling()
        if not instelling or not instelling.email_beheer:
            raise Exception(
                "De beheer_email kan niet worden gevonden, er zijn nog geen instellingen voor aangemaakt"
            )
        context = super().get_context_data(**kwargs)
        context["email_beheer"] = instelling.email_beheer
        return context

    def get_object(self, queryset=None):
        return self.request.user

    def get_initial(self):
        initial = self.initial.copy()
        obj = self.get_object()
        context = obj.profiel.context if hasattr(obj, "profiel") else None
        initial["context"] = context
        initial["group"] = obj.groups.all().first()
        return initial

    def form_valid(self, form):
        MeldingenService().set_gebruiker(
            gebruiker=self.request.user.serialized_instance(),
        )
        messages.success(self.request, "Gebruikersgegevens succesvol opgeslagen.")
        return super().form_valid(form)
