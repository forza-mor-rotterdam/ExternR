from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render


@login_required
@permission_required("authorisatie.beheer_bekijken", raise_exception=True)
def beheer(request):
    env_suffixs = {
        settings.PRODUCTIE: "",
        settings.ACCEPTATIE: "-acc",
        settings.TEST: "-test",
    }
    beheer_url = "/beheer/"
    domain = "forzamor.nl"
    env_urls = [
        (
            f"https://planr{env_suffixs.get(settings.APP_ENV, env_suffixs.get(settings.ACCEPTATIE))}.{domain}{beheer_url}",
            "PlanR",
        ),
        (
            f"https://fixer{env_suffixs.get(settings.APP_ENV, env_suffixs.get(settings.ACCEPTATIE))}.{domain}{beheer_url}",
            "FixeR",
        ),
        (
            f"https://onderwerpen{env_suffixs.get(settings.APP_ENV, env_suffixs.get(settings.ACCEPTATIE))}.{domain}{beheer_url}",
            "Onderwerpen",
        ),
        (
            f"https://ontdbblr{env_suffixs.get(settings.APP_ENV, env_suffixs.get(settings.ACCEPTATIE))}.{domain}{beheer_url}",
            "OntdbblR",
        ),
        (
            f"https://taakr{env_suffixs.get(settings.APP_ENV, env_suffixs.get(settings.ACCEPTATIE))}.{domain}{beheer_url}",
            "TaakR",
        ),
    ]

    return render(
        request,
        "beheer/beheer.html",
        {
            "env_urls": env_urls,
        },
    )
