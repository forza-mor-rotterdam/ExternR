import uuid

from django.contrib.gis.db import models


class BasisModel(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    aangemaakt_op = models.DateTimeField(editable=False, auto_now_add=True)
    aangepast_op = models.DateTimeField(editable=False, auto_now=True)

    class Meta:
        abstract = True
