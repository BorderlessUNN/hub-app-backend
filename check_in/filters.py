import django_filters as filters

from check_in.models import CheckIn


class CheckInFilter(filters.FilterSet):
    # Accepts: ?created_at=YYYY-MM-DD
    created_at = filters.DateFilter(field_name="created_at", lookup_expr="date")

    class Meta:
        model = CheckIn
        fields = ["created_at",]

