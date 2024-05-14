from django.db.models import Q
from django.template.defaultfilters import slugify


class StandaardFilter:
    _key = None
    _option_key_lookup = None
    _option_value_lookup = None
    _option_value_fallback_lookup = None
    _option_group_lookup = None
    _filter_lookup = None
    _taken = None
    _taken_filtered = None
    _options = None
    _groups = []
    _filter_manager = None
    _selected_options = None
    _foldout_states = []

    def __init__(self, filter_manager, selected_options, foldout_states=[]):
        self._selected_options = selected_options
        self._filter_manager = filter_manager
        self._foldout_states = foldout_states
        self._set_options(selected_options)

    @classmethod
    def key(cls):
        return cls._key

    def get_option_key_lookup(self):
        return self._option_key_lookup

    def get_option_value_lookup(self):
        return (
            self._option_value_lookup
            if self._option_value_lookup
            else self._option_key_lookup
        )

    def get_option_value_fallback_lookup(self):
        return (
            self._option_value_fallback_lookup
            if self._option_value_fallback_lookup
            else self.get_option_value_lookup()
        )

    def get_option_group_lookup(self):
        return (
            self._option_group_lookup
            if self._option_group_lookup
            else self.get_option_value_lookup()
        )

    @classmethod
    def get_filter_lookup(cls):
        return cls._filter_lookup

    @classmethod
    def name(cls):
        return cls._label

    @classmethod
    def group_label(cls):
        return cls._group_label

    @classmethod
    def group_key(cls):
        return cls._group_key

    def _set_options(self, selected_options):
        option_key = self.get_option_key_lookup()
        option_value = self.get_option_value_lookup()
        option_value_fallback = self.get_option_value_fallback_lookup()
        option_group = self.get_option_group_lookup()

        def value_lookup(obj, key, fallback_obj=None):
            if isinstance(obj, dict) and obj.get(key, key):
                return obj.get(key, key)
            if isinstance(fallback_obj, dict) and fallback_obj.get(key, key):
                return fallback_obj.get(key, key)
            if isinstance(obj, (str, int)):
                return obj
            return key

        f_dict = {
            ll[0]: (value_lookup(ll[1], ll[0], ll[2]), ll[3], 0)
            for ll in self._filter_manager.taken.order_by(option_key)
            .values_list(option_key, option_value, option_value_fallback, option_group)
            .distinct(option_key)
        }

        """
        Onderstaande voegt aantallen gevonden taken toe aan de filter opties
        """
        # ff_dict = {
        #     fl[0]: (value_lookup(fl[1], fl[0], fl[2]), fl[3], fl[4])
        #     for fl in self._filter_manager.taken_filtered.order_by(option_key)
        #     .values_list(option_key, option_value, option_value_fallback, option_group)
        #     .annotate(count=Count(option_key))
        # }
        # f_dict.update(ff_dict)
        f_dict = {str(k): v for k, v in f_dict.items() if k}
        if hasattr(self, "_predefined_options"):
            f_dict = {
                o[0]: (o[1], o[1], f_dict.get(o[0], (o[1], o[1], 0))[2])
                for o in self._predefined_options
            }

        def create_option(k, label, filter_label=None):
            return {
                "id": slugify(k),
                "value": k,
                "label": label,
                "filter_label": label if not filter_label else filter_label,
                "checked": str(k) in selected_options,
            }

        self._options = sorted(
            [
                create_option(
                    k, v[0], f"{v[1]} - {v[0]}" if self._option_group_lookup else v[0]
                )
                for k, v in f_dict.items()
            ],
            key=lambda x: x.get("label"),
        )
        if self._option_group_lookup:
            self._groups = [
                {
                    "name": g,
                    "group_key": slugify(g),
                    "folded": f"foldout_{slugify(g)}" in self._foldout_states,
                    "key": self._key,
                    "active": [
                        kk
                        for kk, vv in f_dict.items()
                        if kk in selected_options and g == vv[1]
                    ],
                    "label": self._label,
                    "options": sorted(
                        [
                            create_option(kk, vv[0])
                            for kk, vv in f_dict.items()
                            if g == vv[1]
                        ],
                        key=lambda x: x.get("label"),
                    ),
                }
                for g in list(set([v[1] for k, v in f_dict.items()]))
            ]

    def label(self):
        return self._label if not self._option_group_lookup else self._group_label

    def folded(self):
        return (
            f"foldout_{self._key if not self._option_group_lookup else self._group_key}"
            in self._foldout_states
        )

    def options(self):
        return self._options

    def active(self):
        return self._selected_options

    def groups(self):
        return sorted(self._groups, key=lambda x: x.get("name"))


class BegraafplaatsFilter(StandaardFilter):
    _key = "begraafplaats"
    _option_key_lookup = "taak_zoek_data__begraafplaats"
    _option_value_lookup = (
        "melding__response_json__meta_uitgebreid__begraafplaats__choices"
    )
    _option_value_fallback_lookup = "melding__response_json__signalen_voor_melding__0__meta_uitgebreid__begraafplaats__choices"
    _filter_lookup = "taak_zoek_data__begraafplaats__in"
    _label = "Begraafplaats"


class TaaktypeFilter(StandaardFilter):
    _key = "taken"
    _option_key_lookup = "taaktype__id"
    _option_value_lookup = "taaktype__omschrijving"
    _filter_lookup = "taaktype__id__in"
    _label = "Taak"


class TaakStatusFilter(StandaardFilter):
    _key = "taak_status"
    _option_key_lookup = "taakstatus__naam"
    _option_value_lookup = "taakstatus__naam"
    _filter_lookup = "taakstatus__naam__in"
    _label = "Taakstatus"
    _predefined_options = (
        ("nieuw", "Nieuw"),
        ("voltooid", "Voltooid"),
    )


class WijkBuurtFilter(StandaardFilter):
    _key = "buurt"
    _option_key_lookup = "taak_zoek_data__buurtnaam"
    _option_group_lookup = "taak_zoek_data__wijknaam"
    _filter_lookup = "taak_zoek_data__buurtnaam__in"
    _label = "Buurten"
    _group_key = "wijken"
    _group_label = "Wijken & buurten"


class ZoekFilter(StandaardFilter):
    _key = "q"
    _label = "Zoek"

    @classmethod
    def get_filter_lookup(cls, search_query):
        return Q(taak_zoek_data__straatnaam__iregex=search_query) | Q(
            taak_zoek_data__bron_signaal_ids__icontains=search_query
        )

    def _set_options(self, selected_options):
        # For search filter, we don't need to set specific options
        self._options = []


class FilterManager:
    _taken = None
    _taken_filtered = None
    _available_filter_classes = (
        BegraafplaatsFilter,
        TaaktypeFilter,
        TaakStatusFilter,
        WijkBuurtFilter,
    )
    _foldout_states = None

    def __init__(self, taken, active_filters, foldout_states=[]):
        self._taken = taken
        self._active_filters = {
            k: v
            for k, v in active_filters.items()
            if isinstance(v, (list, tuple)) and self._get_filter_class(k)
        }
        self._foldout_states = foldout_states

    def _set_filter_options(self):
        self._filter_options = [
            self._get_filter_class(k)(self, v, self._foldout_states)
            for k, v in self._active_filters.items()
        ]

    def _get_filter_class(self, filter_key):
        filter_classes = self._available_filter_classes
        filter_classes += (ZoekFilter,)
        return {cls.key(): cls for cls in filter_classes}.get(filter_key)

    @property
    def taken(self):
        return self._taken

    @property
    def taken_filtered(self):
        return self._taken_filtered

    @classmethod
    def available_filter_names(cls):
        return [f.key() for f in cls._available_filter_classes]

    @property
    def active_filter_count(self):
        return len([vv for k, v in self._active_filters.items() for vv in v])

    @property
    def active_filters(self):
        return self._active_filters

    def filter_taken(self):
        search_query = self._active_filters.pop("q", "")
        queryset_filter = Q()

        if search_query and search_query[0]:
            search_conditions = ZoekFilter.get_filter_lookup(search_query[0])
            queryset_filter &= search_conditions

        for k, v in self._active_filters.items():
            if v:
                filter_class = self._get_filter_class(k)
                if filter_class:
                    queryset_filter &= Q(**{filter_class.get_filter_lookup(): v})

        self._taken_filtered = self._taken.filter(queryset_filter)
        self._set_filter_options()
        return self._taken_filtered

    def filters(self, foldout_states=[]):
        return self._filter_options
