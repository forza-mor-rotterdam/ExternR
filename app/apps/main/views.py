import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

logger = logging.getLogger(__name__)


def http_403(request):
    return render(
        request,
        "403.html",
    )


def http_404(request):
    return render(
        request,
        "404.html",
    )


def http_500(request):
    return render(
        request,
        "500.html",
    )


# Verander hier de instellingen voor de nieuwe homepagina.
def root(request):
    if request.user.is_authenticated:
        if request.user.has_perms(["authorisatie.beheer_bekijken"]):
            return redirect(reverse("beheer"), False)
        return render(
            request,
            "home_ingelogd.html",
            {},
        )
    return render(
        request,
        "home.html",
        {},
    )


@login_required
def ui_settings_handler(request):
    profiel = request.user.profiel
    if request.POST:
        profiel.ui_instellingen.update(
            {"fontsize": request.POST.get("fontsize", "fz-medium")}
        )
        profiel.save()

    return render(
        request,
        "snippets/form_pageheader.html",
        {"profile": profiel},
    )
