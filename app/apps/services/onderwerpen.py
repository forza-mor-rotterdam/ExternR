import logging

from apps.services.basis import BasisService
from django.template.loader import get_template
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)


def render_onderwerp(onderwerp_url, standaar_naam=None):
    onderwerp = OnderwerpenService().get_onderwerp(onderwerp_url)
    standaard_naam = onderwerp.get(
        "name", "Niet gevonden!" if not standaar_naam else standaar_naam
    )
    if onderwerp.get("priority") == "high":
        spoed_badge = get_template("badges/spoed.html")
        return mark_safe(f"{standaard_naam}{spoed_badge.render()}")
    return standaard_naam


class OnderwerpenService(BasisService):
    def get_onderwerp(self, url) -> dict:
        return self.do_request(url, cache_timeout=60 * 10, raw_response=False)
