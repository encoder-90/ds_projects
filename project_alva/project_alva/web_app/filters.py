from django_filters import FilterSet
from .models import History


class HistoryFilter(FilterSet):
    class Meta:
        model = History
        exclude = ["id", "user", "currency"]