import json
import logging
import os

import requests
from django import template
from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.cache import cache
from requests import Request, Response
from utils.datetime import stringdatetime_naar_datetime

register = template.Library()
logger = logging.getLogger(__name__)


@register.filter
def replace_comma_by_dot(value):
    return str(value).replace(",", ".")


@register.filter
def to_datetime(value):
    if value and isinstance(value, str):
        return stringdatetime_naar_datetime(value)
    return value


@register.filter
def to_timestamp(value):
    try:
        return int(value.timestamp())
    except Exception as e:
        logger.error(f"No datatime instance, value={value}: error={e}")


@register.filter
def json_encode(value):
    if isinstance(value, Point):
        return value.geojson
    return json.dumps(value)


@register.filter
def json_loads(value):
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return None


@register.filter
def replace_n(value):
    return value.replace("\\n", "<br/>").replace("?", "?<br/>")


@register.simple_tag
def vind_in_dict(op_zoek_dict, key):
    if not isinstance(op_zoek_dict, dict):
        return key
    result = op_zoek_dict.get(key, op_zoek_dict.get(str(key), key))
    if isinstance(result, (list, tuple)):
        return result[0]
    return result


@register.filter
def adres_order_nummer(taak, taken_sorted):
    return taken_sorted.get(taak.id, taak.id)


@register.filter
def mor_core_url(initial_url, signed_data=None):
    return (
        f"{settings.MOR_CORE_URL_PREFIX}{initial_url}?signed-data={signed_data}"
        if signed_data
        else f"{settings.MOR_CORE_URL_PREFIX}{initial_url}"
    )


@register.filter
def mor_core_protected_url(initial_url):
    return f"{settings.MOR_CORE_PROTECTED_URL_PREFIX}{initial_url}"


@register.filter(name="python_any")
def python_any(values):
    if values:
        return any(values)
    return values


@register.filter
def file_exists(file_path):
    return os.path.isfile(
        os.path.join(settings.BASE_DIR, "apps/main/templates/", file_path)
    )


@register.filter("startswith")
def startswith(text, starts):
    if isinstance(text, str):
        return text.startswith(starts)
    return False


@register.filter("get_svg_path")
def get_svg_pathl(url):
    method = "get"
    action: Request = getattr(requests, method)
    cache_timeout = 60 * 60

    try:
        cache_key = url
        response = cache.get(url)
        if not response:
            response: Response = action()
            if int(response.status_code) == 200:
                cache.set(cache_key, response, cache_timeout)
        if response:
            return response.text
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
