import pandas as pd
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import render, redirect
from web_app.models import ContactMessage
from django_tables2 import SingleTableView
from django_tables2.export.views import ExportMixin

from machine_learning.model import xgb_model, stats
from project_alva import settings
from .forms import UserRegisterForm, PredictionForm
from .models import History
from .tables import HistoryTable


def home(request):
    user = request.user
    if user.is_authenticated:
        if user.has_subscription():
            return redirect("dashboard")
    return render(request, "web_app/home.html", {"selectedTab": "home"})


@login_required(login_url=settings.LOGIN_URL)
def dashboard(request):
    user = request.user
    # Get the latest 5 prediction resutls
    results = History.objects.filter(user=user).order_by("-id").all()[:5]
    is_subscribed = user.has_subscription()
    return render(request, "web_app/dashboard.html", {"results": results, "is_subscribed": is_subscribed})


def about(request):
    if request.method == "POST":
        name = request.POST.get('firstName') + " " + request.POST.get('lastName')
        email = request.POST.get('email')
        title = request.POST.get('title')
        message = request.POST.get('message')
        c = ContactMessage(fullname=name, email=email, title=title, message=message)
        c.save()

        message = """\
        From: %s

        %s
        """ % (email + ' (' + name + ')', message)

        emailToSend = EmailMessage(title, message, to=['alvatest01@gmail.com'])
        emailToSend.send()
        messages.success(request, "Successfully sent email")
        return redirect("home")
    return render(request, "web_app/about.html", {"selectedTab": "about"})


@login_required(login_url=settings.LOGIN_URL)
def subscription(request):
    user = request.user

    if request.method == "POST":
        if "basic" in request.POST:
            value = request.POST.get("selectBasic")
        elif "premium" in request.POST:
            value = request.POST.get("selectPremium")
        elif "addPredictions" in request.POST:
            user.add_predictions()
            messages.success(request, "Extra 50 predictions successfully added!")
            return redirect("home")

        if value is None:
            messages.error(request, "Please select a valid duration!")
        else:
            user.make_subscription(value)
            messages.success(
                request,
                "{0} subscription successfully applied!".format(user.subscription.name),
            )
            return redirect("home")

    return render(request, "web_app/subscription.html", {"selectedTab": "subscription"})


# https://docs.djangoproject.com/en/3.1/topics/auth/default/#the-login-required-decorator
@login_required(login_url=settings.LOGIN_URL)
def prediction(request):
    user = request.user
    is_subscribed = user.has_subscription()
    has_predictions = user.has_predictions_left()
    if is_subscribed and has_predictions:
        # User has an active subscription
        if request.method == "POST":
            form = PredictionForm(request.POST)
            if form.is_valid():
                with transaction.atomic():
                    price = get_predicted_estate_price(form)
                    squareMeters = form.cleaned_data["squareMeters"]
                    priceSQM = price / squareMeters
                    priceSQM = int(round(priceSQM, 0))
                    prediction = create_prediction(user, form, price, priceSQM)
                    messages.success(request, "Prediction successfuly made!")
                    return redirect("prediction_overview", pk=prediction.id)
        else:
            form = PredictionForm()
        return render(
            request,
            "web_app/prediction.html",
            {"selectedTab": "prediction", "form": form},
        )

    # User is not subscribed or does not have any more subscriptions
    messages.info(request, "You do not have an active subscription or predictions left")
    return redirect("subscription")


@login_required(login_url=settings.LOGIN_URL)
def prediction_overview(request, pk):
    user = request.user
    is_subscribed = user.has_subscription()
    has_predictions = user.has_predictions_left()
    if is_subscribed and has_predictions:
        prediction = History.objects.filter(id=pk).first()
        district = str(prediction.district)
        prediction_result = prediction.pricePrediction

        data = stats.get_data_subset_for_district(district)
        rows = stats.get_number_samples_mapper()

        district_df = stats.get_data_subset_for_district(district)
        file_name_bar_chart = stats.get_svg_bar_plot_district_mean_price_per_apartment_type(district_df,
                                                                                            prediction_result)
        file_name_bar_chart = f"web_app/media/{file_name_bar_chart}"

        file_name_pie_chart = stats.get_svg_pie_chart_by_number_properties_for_sale(district_df)
        file_name_pie_chart = f"web_app/media/{file_name_pie_chart}"

        # Decrease amount of subscriptions
        user.remove_prediction()
        return render(request, "web_app/overview.html",
                      {"prediction": prediction, "file_name_bar_chart": file_name_bar_chart,
                       "file_name_pie_chart": file_name_pie_chart, "rows": rows, "district": district})

    # User is not subscribed or does not have any more subscriptions
    messages.info(request, "You do not have an active subscription or predictions left")
    return redirect("subscription")


class HistoryListView(ExportMixin, LoginRequiredMixin, SingleTableView):
    model = History
    table_class = HistoryTable
    export_name = "results_data"
    exclude_columns = ("overview",)
    template_name = "web_app/results.html"

    def get_queryset(self):
        return History.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(HistoryListView, self).get_context_data(**kwargs)
        context["selectedTab"] = "results"
        return context


# # Use this initialization for filtering
# class HistoryListView(LoginRequiredMixin, SingleTableMixin, FilterView):
#     model = History
#     table_class = HistoryTable
#     template_name = 'web_app/results.html'
#     filterset_class = HistoryFilter

#     def get_queryset(self):
#         return History.objects.filter(user=self.request.user)

def logout_view(request):
    logout(request)
    return redirect("login")


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("inputEmail")
        password = request.POST.get("inputPassword")
        user = authenticate(request, email=email, password=password)
        if user is not None:
            # A backend authenticated the credentials
            login(request, user)
            return redirect("home")
        else:
            # No backend authenticated the credentials
            messages.error(request, "Invalid credentials")
            return redirect("login")
    else:
        return render(request, "web_app/auth/login.html")


def register_view(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            email = form.cleaned_data.get("email")
            messages.success(request, f"Account created for {email} ")
            login(request, user)
            return redirect("home")
    else:
        form = UserRegisterForm()
    return render(request, "web_app/auth/register.html", {"form": form})


def get_predicted_estate_price(form):
    # Load data
    data = {
        "apartment_type": [str(form.cleaned_data["apartmentType"])],
        "district": [str(form.cleaned_data["district"])],
        "price": [100.0],
        "sqr_m": [form.cleaned_data["squareMeters"]],
        "price_sqrm": [100.0],
        "currency": ["EUR"],
        "year": [float(form.cleaned_data["year"])],
        "floor": [float(form.cleaned_data["floor"])],
        "gas": [int(form.cleaned_data["gas"])],
        "heating": [int(form.cleaned_data["heating"])],
        "construction_type": [str(form.cleaned_data["constructionType"])],
        "furnished": [int(form.cleaned_data["furnished"])],
        "entrance_control": [int(form.cleaned_data["entranceControl"])],
        "security": [int(form.cleaned_data["security"])],
        "passageway": [int(form.cleaned_data["passageway"])],
    }
    dataframe = pd.DataFrame(data)
    predicted_price = xgb_model.make_prediction_web_app(dataframe)
    return predicted_price


@transaction.atomic
def create_prediction(request_user, form, predictedPrice, predictedPriceSQM):
    prediction = History.objects.create(
        apartmentType=form.cleaned_data["apartmentType"],
        constructionType=form.cleaned_data["constructionType"],
        district=form.cleaned_data["district"],
        pricePrediction=predictedPrice,
        priceSQM=predictedPriceSQM,
        squareMeters=form.cleaned_data["squareMeters"],
        year=form.cleaned_data["year"],
        floor=form.cleaned_data["floor"],
        gas=form.cleaned_data["gas"],
        heating=form.cleaned_data["heating"],
        furnished=form.cleaned_data["furnished"],
        entranceControl=form.cleaned_data["entranceControl"],
        security=form.cleaned_data["security"],
        passageway=form.cleaned_data["passageway"],
        user=request_user,
        currency="EUR"
    )
    prediction.save()
    return prediction
