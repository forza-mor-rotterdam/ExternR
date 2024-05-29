from datetime import timedelta

from django.db.models import Q, QuerySet
from django.utils import timezone


class TaakQuerySet(QuerySet):
    def _get_taak_types(self, user):
        return user.profiel.context.taaktypes.all() if user.profiel.context else []

    def get_taken_recent(self, user):
        taak_types = self._get_taak_types(user)
        return self.filter(
            Q(afgesloten_op__gt=timezone.now() - timedelta(days=3))
            & Q(taaktype__in=taak_types)
            | Q(afgesloten_op__isnull=True) & Q(taaktype__in=taak_types),
        ).order_by("-aangemaakt_op")

    def get_taken_nieuw(self, user):
        taak_types = self._get_taak_types(user)
        return self.filter(
            afgesloten_op__isnull=True,
            taaktype__in=taak_types,
        ).order_by("-aangemaakt_op")

    def get_taken_voltooid(self, user):
        from apps.taken.models import Taak

        taak_types = self._get_taak_types(user)
        return self.filter(
            afgesloten_op__isnull=False,
            taaktype__in=taak_types,
            resolutie__in=[
                Taak.ResolutieOpties.NIET_OPGELOST,
                Taak.ResolutieOpties.OPGELOST,
                Taak.ResolutieOpties.NIET_GEVONDEN,
            ],
        ).order_by("-afgesloten_op")
