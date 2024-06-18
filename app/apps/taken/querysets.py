from django.db.models import QuerySet


class TaakQuerySet(QuerySet):
    def get_taken_recent(self, user):
        return self.filter(bezig_met_verwerken=False).order_by("-aangemaakt_op")
