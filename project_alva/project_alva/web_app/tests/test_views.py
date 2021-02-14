from django.test import TestCase, Client
from web_app.models import Subscription, CustomUser
from django.shortcuts import reverse


class ViewTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(email="testuser@test.com")
        self.oneMonthSubscription = Subscription.subscriptionTypes.create(
            subscriptionType="OneMonth", durationMonths=1, name=""
        )
        self.client = Client()

    def test_dashboard_user_not_logged_in(self):
        """
        Test if the user can access the dashboard if he is not logged in.
        """
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/dashboard")

    def test_dashboard_user_logged_in(self):
        """
        Test if the user can access the dashboard if he is logged in.
        """
        self.client.force_login(self.user)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "web_app/dashboard.html")

    def test_home_user_logged_in_no_subscription(self):
        """
        Test if user without subscription is presented with the home page when
        navigating to it.
        """
        self.client.force_login(self.user)
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "web_app/home.html")

    def test_home_user_logged_in_and_subscribed(self):
        """
        Test if user with a subscription is presented with the dashboard page
        when navigating to it.
        """
        self.client.force_login(self.user)
        self.user.make_subscription(self.oneMonthSubscription.id)
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/dashboard")

    def test_prediction_page_no_subscription(self):
        """
        Test if the user can access the prediction page without an active
        subscription.
        """
        self.client.force_login(self.user)
        response = self.client.get(reverse("prediction"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/subscription")

    def test_prediction_page_subscription_present_no_predictions_left(self):
        """
        Test if the user can access the prediction page with an active
        subscription but with no predictions left to run.
        """
        self.client.force_login(self.user)
        self.user.make_subscription(self.oneMonthSubscription.id)
        self.user.predictions_left = 0
        self.user.save()
        response = self.client.get(reverse("prediction"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/subscription")

    def test_prediction_page_all_preconditions_present(self):
        """
        Test if the user can access the prediction page with all
        preconditions met.
        """
        self.client.force_login(self.user)
        self.user.make_subscription(self.oneMonthSubscription.id)
        response = self.client.get(reverse("prediction"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "web_app/prediction.html")

    def test_logout(self):
        """
        Test if the logout functionality loads the correct view.
        """
        self.client.force_login(self.user)
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/")
