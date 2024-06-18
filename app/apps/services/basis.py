import logging
from urllib.parse import urlencode

import requests
from django.contrib import messages
from django.core.cache import cache
from requests import Request, Response

logger = logging.getLogger(__name__)


class BasisService:
    _api_base_url = None
    _timeout: tuple[int, ...] = (10, 20)
    _api_path: str = "/api/v1"
    _default_error_message = "Er ging iets mis met het ophalen van data!"

    def __init__(self, *args, **kwargs: dict):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    class BasisUrlFout(Exception):
        ...

    class AntwoordFout(Exception):
        ...

    class DataOphalenFout(Exception):
        ...

    class NaarJsonFout(Exception):
        ...

    def get_url(self, url):
        return url

    def get_headers(self):
        return {}

    def naar_json(self, response):
        try:
            return response.json()
        except Exception as e:
            return {"bericht": f"{e}, response text: {response.text}"}

    def do_request(
        self,
        url,
        method="get",
        data={},
        params={},
        raw_response=True,
        cache_timeout=0,
        expected_status_code=200,
        force_cache=False,
    ) -> Response | dict:
        action: Request = getattr(requests, method)
        url = self.get_url(url)
        response = None
        action_params: dict = {
            "url": url,
            "headers": self.get_headers(),
            "json": data,
            "params": params,
            "timeout": self._timeout,
        }
        cache_key = f"{url}?{urlencode(params)}"
        if force_cache:
            cache.delete(cache_key)

        if cache_timeout and method == "get" and not force_cache:
            response = cache.get(cache_key)
            if (
                hasattr(response, "status_code")
                and getattr(response, "status_code") != 200
            ):
                response = None

        if not response:
            try:
                response: Response = action(**action_params)
            except Exception as e:
                cache.delete(cache_key)
                logger.error(f"error: {e}")
                if self.request:
                    messages.error(self.request, self._default_error_message)
                return {"error": f"{e}"}

            if cache_timeout and method == "get" and response.status_code == 200:
                logger.debug(
                    f"set cache for: url={cache_key}, cache_timeout={cache_timeout}"
                )
                cache.set(cache_key, response, cache_timeout)

        if raw_response:
            return response
        if response.status_code != expected_status_code:
            logger.error(
                f"Antwoord: {self.naar_json(response)}, status code: {response.status_code}"
            )
            if self.request:
                messages.error(self.request, self.naar_json(response).get("detail"))
            return {
                "error": f"Antwoord: {self.naar_json(response)}, status code: {response.status_code}"
            }
        return self.naar_json(response)
