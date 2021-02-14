from django.test import TestCase
from web_app.models import (
    ApartmentType,
    District,
    ConstructionType,
)
from web_app.forms import PredictionForm, UserRegisterForm


class FormTestCase(TestCase):
    def setUp(self):
        self.apartmentType = ApartmentType.objects.create(apartmentType="2-STAEN")
        self.constructionType = ConstructionType.objects.create(constructionType="Brick")
        self.district = District.objects.create(name="Vitosha")

    def test_prediction_form_valid(self):
        """
        Test if the Prediction Form validates the data.
        """
        form_data = {
            "apartmentType": self.apartmentType,
            "constructionType": self.constructionType,
            "district": self.district,
            "squareMeters": 100,
            "year": 2010,
            "floor": 5,
            "gas": 1,
            "heating": 1,
            "furnished": 0,
            "entranceControl": 0,
            "security": 1,
            "passageway": 0
        }
        form = PredictionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_prediction_form_invalid(self):
        """
        Test if the Prediction Form validates the data.
        """
        form_data = {
            "constructionType": self.constructionType,
            "district": self.district,
            "squareMeters": 100,
            "year": 5000,
            "floor": 5,
            "gas": 1,
            "heating": 1,
            "furnished": 0,
            "entranceControl": 0,
            "security": 1,
            "passageway": 0
        }
        form = PredictionForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_user_form_valid(self):
        """
        Test if the User Register Form validates the data.
        """
        form_data = {
            "email": "test1@test.com",
            "password1": "alvaproject123",
            "password2": "alvaproject123"
        }
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_user_form_invalid(self):
        """
        Test if the User Register Form validates the data.
        """
        form_data = {
            "email": "test1",
            "password1": "alvaproject123",
            "password2": "alvaproject123"
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
