import logging
from urllib.parse import urlencode, urlparse

import requests
from apps.instellingen.models import Instelling
from django.core.cache import cache
from requests import Request, Response

logger = logging.getLogger(__name__)


class MeldingenService:
    _base_url = None
    _timeout: tuple[int, ...] = (10, 20)
    _api_path: str = "/api/v1"
    _token_api: str = "/api-token-auth/"
    _use_token = True
    _token_timeout = 0

    class BasisUrlFout(Exception):
        ...

    class DataOphalenFout(Exception):
        ...

    def __init__(self, *args, **kwargs: dict):
        instelling = Instelling.actieve_instelling()
        if not instelling:
            raise Exception(
                "De MOR-Core instellingen kunnen niet worden gevonden, Er zijn nog geen instellingen aangemaakt"
            )
        self._use_token = (
            instelling.mor_core_gebruiker_email
            and instelling.mor_core_gebruiker_wachtwoord
        )
        self._token_timeout = instelling.mor_core_token_timeout
        self._base_url = instelling.mor_core_basis_url
        super().__init__(*args, **kwargs)

    def get_url(self, url):
        url_o = urlparse(url)
        if not url_o.scheme and not url_o.netloc:
            return f"{self._base_url}{url}"
        if f"{url_o.scheme}://{url_o.netloc}" == self._base_url:
            return url
        raise MeldingenService.BasisUrlFout(f"url: {url}, basis_url: {self._base_url}")

    def haal_token(self):
        meldingen_token = cache.get("meldingen_token")
        if not self._token_timeout:
            cache.delete("meldingen_token")

        if not meldingen_token:
            instelling = Instelling.actieve_instelling()
            if not instelling:
                raise Exception(
                    "De MOR-Core instellingen kunnen niet worden gevonden, Er zijn nog geen instellingen aangemaakt"
                )
            token_response = requests.post(
                f"{self._base_url}{self._token_api}",
                json={
                    "username": instelling.mor_core_gebruiker_email,
                    "password": instelling.mor_core_gebruiker_wachtwoord,
                },
            )
            if token_response.status_code == 200:
                meldingen_token = token_response.json().get("token")
                if self._token_timeout:
                    cache.set("meldingen_token", meldingen_token, self._token_timeout)
            else:
                raise MeldingenService.DataOphalenFout(
                    f"status code: {token_response.status_code}, response text: {token_response.text}"
                )

        return meldingen_token

    def get_headers(self):
        headers = {}
        if self._use_token:
            headers.update({"Authorization": f"Token {self.haal_token()}"})
        return headers

    def do_request(
        self,
        url,
        method="get",
        data={},
        params={},
        raw_response=True,
        cache_timeout=0,
        stream=False,
    ) -> Response | dict:
        action: Request = getattr(requests, method)
        url = self.get_url(url)
        action_params: dict = {
            "url": url,
            "headers": self.get_headers(),
            "json": data,
            "params": params,
            "timeout": self._timeout,
            "stream": stream,
        }

        if cache_timeout and method == "get":
            cache_key = f"{url}?{urlencode(params)}"
            response = cache.get(cache_key)
            if not response:
                response: Response = action(**action_params)
                if int(response.status_code) == 200:
                    cache.set(cache_key, response, cache_timeout)
        else:
            response: Response = action(**action_params)

        if raw_response:
            return response
        return self.naar_json(response)

    def get_melding_lijst(self, query_string=""):
        return self.do_request(
            f"{self._api_path}/melding/?{query_string}", raw_response=False
        )

    def get_melding(self, id, query_string=""):
        return self.do_request(
            f"{self._api_path}/melding/{id}/?{query_string}", raw_response=False
        )

    def get_by_uri(self, uri):
        return self.do_request(uri)

    def taak_aanmaken(
        self,
        melding_uuid,
        taaktype_url,
        titel,
        bericht=None,
        gebruiker=None,
        additionele_informatie={},
    ):
        data = {
            "taaktype": taaktype_url,
            "titel": titel,
            "bericht": bericht,
            "gebruiker": gebruiker,
            "additionele_informatie": additionele_informatie,
        }
        return self.do_request(
            f"{self._api_path}/melding/{melding_uuid}/taakopdracht/",
            method="post",
            data=data,
        )

    def taak_status_aanpassen(
        self,
        taakopdracht_url,
        status,
        resolutie=None,
        omschrijving_intern=None,
        bijlagen=[],
        gebruiker=None,
        uitvoerder=None,
        naar_niet_opgelost=False,
    ):
        data = {
            "taakstatus": {
                "naam": status,
            },
            "resolutie": resolutie,
            "omschrijving_intern": omschrijving_intern,
            "bijlagen": bijlagen,
            "gebruiker": gebruiker,
        }
        if naar_niet_opgelost:
            data.update({"externr_niet_opgelost": True})
        if uitvoerder:
            data.update({"uitvoerder": uitvoerder})
        return self.do_request(
            f"{taakopdracht_url}status-aanpassen/",
            method="patch",
            data=data,
        )

    def taak_gebeurtenis_toevoegen(
        self,
        taakopdracht_url,
        gebeurtenis_type=None,
        omschrijving_intern=None,
        bijlagen=[],
        gebruiker=None,
    ):
        data = {
            "gebeurtenis_type": gebeurtenis_type,
            "omschrijving_intern": omschrijving_intern,
            "bijlagen": bijlagen,
            "gebruiker": gebruiker,
        }
        return self.do_request(
            f"{taakopdracht_url}gebeurtenis-toevoegen/", method="post", data=data
        )

    def get_gebruiker(self, gebruiker_email):
        return self.do_request(
            f"{self._api_path}/gebruiker/{gebruiker_email}/",
            method="get",
            cache_timeout=60 * 60 * 24,
        )

    def set_gebruiker(self, gebruiker):
        return self.do_request(
            f"{self._api_path}/gebruiker/", method="post", data=gebruiker
        )

    def get_taakopdracht_data(self, taakopdracht_url):
        response = self.do_request(taakopdracht_url)
        return response

    def afbeelding_ophalen(self, afbeelding_url: str, stream=False):
        return self.do_request(afbeelding_url, stream=stream)
