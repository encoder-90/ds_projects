from django.urls import path
from . import views


urlpatterns = [
    # Paths
    path("", views.home, name="home"),
    path("home", views.home, name="home"),
    path("about", views.about, name="about"),
    path("subscription", views.subscription, name="subscription"),
    path("prediction", views.prediction, name="prediction"),
    path("results", views.HistoryListView.as_view(), name="results"),
    path('overview/<int:pk>', views.prediction_overview, name="prediction_overview"),
    path("dashboard", views.dashboard, name="dashboard"),

    # Authentication paths
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
]
