import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor
from .models import History


class HistoryTable(tables.Table):
    export_formats = ['csv']
    overview = tables.LinkColumn('prediction_overview', text='Rerun', args=[A('pk')], attrs={'a': {'class': 'btn btn-primary'}})

    class Meta:
        model = History
        exclude = ["id", "user", "currency"]