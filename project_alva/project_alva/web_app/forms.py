from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from .models import CustomUser, History, ApartmentType, ConstructionType, District


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = CustomUser
        fields = ["email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)

        # Removes annoying helper messages. Crispy messages are still shown.
        for fieldname in ["email", "password1", "password2"]:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].label = ""

        self.fields["email"].widget = forms.EmailInput(attrs={"placeholder": "Email*"})
        self.fields["password1"].widget = forms.PasswordInput(
            attrs={"placeholder": "Password*", "autocomplete": "new-password"}
        )
        self.fields["password2"].widget = forms.PasswordInput(
            attrs={
                "placeholder": "Password confirmation*",
                "autocomplete": "new-password",
            }
        )


class PredictionForm(ModelForm):
    apartmentType = forms.ModelChoiceField(
        queryset=ApartmentType.objects.all(), empty_label="Apartment Type*"
    )
    constructionType = forms.ModelChoiceField(
        queryset=ConstructionType.objects.all(), empty_label="Construction Type*"
    )
    district = forms.ModelChoiceField(
        queryset=District.objects.all(), empty_label="District*"
    )
    

    class Meta:
        model = History
        exclude = ["user", "currency", "pricePrediction", "priceSQM", "graph"]
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(PredictionForm, self).__init__(*args, **kwargs)

        # Removes annoying helper messages. Crispy messages are still shown.
        for fieldname in self.fields:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].label = ""

        self.fields["squareMeters"].widget.attrs["placeholder"] = "Square meters"
        self.fields["year"].widget.attrs["placeholder"] = "Year built"
        self.fields["floor"].widget.attrs["placeholder"] = "Floor"

        self.fields["gas"].label = "Gas"
        self.fields["heating"].label = "Heating"
        self.fields["furnished"].label = "Furnished"
        self.fields["entranceControl"].label = "Entrance Control"
        self.fields["security"].label = "Security"
        self.fields["passageway"].label = "Passageway"
