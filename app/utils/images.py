# thumbnailname.py

import os.path

from django.conf import settings
from django.utils import timezone
from sorl.thumbnail.base import ThumbnailBackend as SorlThumbnailBackend
from sorl.thumbnail.conf import settings as sorl_settings


def get_date_file_path():
    return timezone.now().strftime("%Y/%m/%d")


def get_upload_path(instance, filename):
    return get_upload_path_base(filename)


def get_upload_path_base(filename):
    return os.path.join(settings.BESTANDEN_PREFIX, get_date_file_path(), filename)


class ThumbnailBackend(SorlThumbnailBackend):
    def _get_thumbnail_filename(self, source, geometry_string, options):
        filename, _ext = os.path.splitext(os.path.basename(source.name))
        filename_full = f"{filename}_{geometry_string}.jpg"
        return os.path.join(
            sorl_settings.THUMBNAIL_PREFIX, get_date_file_path(), filename_full
        )
