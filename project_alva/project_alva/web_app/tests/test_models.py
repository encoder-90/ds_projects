from dateutil.relativedelta import relativedelta
from django.test import TestCase
from django.utils import timezone
from web_app.models import Subscription, CustomUser


class ModelTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(email="testuser@test.com")
        self.oneMonthSubscription = Subscription.subscriptionTypes.create(
            subscriptionType="BasicOneMonth", durationMonths=1, name=""
        )
        self.premiumOneMonthSubscription = Subscription.subscriptionTypes.create(
            subscriptionType="PremiumOneMonth", durationMonths=1, name=""
        )
        self.premiumOneMonthSubscription.id = 4
        self.premiumOneMonthSubscription.save()

    def test_subscription_str_method(self):
        """
        Test if the Subscription __str__() method return correct
        string value.
        """
        string = str(self.oneMonthSubscription)
        self.assertEqual(string, "BasicOneMonth")

    def test_customUser_predictions_left_setter(self):
        """
        Test if customUser predictions left setter works
        correctly.
        """
        self.user.predictions_left = 50
        result = self.user.predictionsLeft = 50
        self.assertEquals(result, 50)

    def test_customUser_predictions_left_getter(self):
        """
        Test if customUser predictions left getter works
        correctly.
        """
        result = self.user.predictions_left
        self.assertEquals(result, 0)

    def test_customUser_has_subscription_return_false_when_no_subscription(self):
        """
        Test if customUser has_subscription method works
        correctly when subscription is None.
        """
        result = self.user.has_subscription()
        self.assertFalse(result)

    def test_customUser_has_subscription_false_when_subscription_expired(self):
        """
        Test if customUser has_subscription method works
        correctly when subscription is expired.
        """
        self.user.subscription = self.oneMonthSubscription
        self.user.subscriptionEndDate = (timezone.now() - relativedelta(days=5)).date()
        result = self.user.has_subscription()
        self.assertFalse(result)
        self.assertEquals(self.user.subscriptionStartDate, None)
        self.assertEquals(self.user.subscriptionEndDate, None)
        self.assertEquals(self.user.subscription, None)

    def test_customUser_has_subscription_true_when_not_null_not_expired(self):
        """
        Test if customUser has_subscription method works
        correctly when subscription is not None and not expired.
        """
        self.user.subscription = self.oneMonthSubscription
        self.user.subscriptionEndDate = timezone.now().date()
        result = self.user.has_subscription()
        self.assertTrue(result)

    def test_customUser_has_predictions_left_true_when_pr_left_gr_0(self):
        """
        Test if customUser has_predictions_left method works
        correctly when pr left are greater than 0.
        """
        self.user.predictions_left = 1
        result = self.user.has_predictions_left()
        self.assertTrue(result)

    def test_customUser_has_predictions_left_false_when_pr_left_eq_0(self):
        """
        Test if customUser has_predictions_left method works
        correctly when pr left are equal to 0.
        """
        result = self.user.has_predictions_left()
        self.assertFalse(result)

    def test_customUser_make_subscription_subscription_is_made(self):
        """
        Test if customUser make_subscription correctly assigns
        subscription to user
        """
        self.user.make_subscription(1)
        result = self.user.subscription
        self.assertEquals(result, self.oneMonthSubscription)

    def test_customUser_make_subscription_correct_subscriptionStartDate(self):
        """
        Test if customUser make_subscription correctly assigns
        subscriptionStartDate
        """
        self.user.make_subscription(1)
        result = self.user.subscriptionStartDate.replace(microsecond=0)
        expected = timezone.now().replace(microsecond=0)
        self.assertEquals(result, expected)

    def test_customUser_make_subscription_correct_subscriptionEndDate_when_no_subs(self):
        """
        Test if customUser make_subscription correctly assigns
        subscriptionEndDate when there is not active subscription.
        """
        self.user.make_subscription(1)
        result = self.user.subscriptionEndDate.replace(microsecond=0)
        expected = (self.user.subscriptionStartDate + relativedelta(
            months=self.oneMonthSubscription.durationMonths)).replace(microsecond=0)
        self.assertEquals(result, expected)

    def test_customUser_make_subscription_correct_subscriptionEndDate_when_subs(self):
        """
        Test if customUser make_subscription correctly assigns
        subscriptionEndDate when there already
        is an active subscription.
        """
        self.user.make_subscription(1)
        expected = self.user.subscriptionEndDate.replace(microsecond=0)
        self.user.make_subscription(1)
        result = (expected + relativedelta(
            months=self.oneMonthSubscription.durationMonths)).replace(microsecond=0)
        expected += relativedelta(months=1)
        self.assertEquals(expected, result)

    def test_customUser_make_subscription_correct_basic_predictions_left_distribution(self):
        """
        Test if customUser make_subscription correctly assigns
        predictions left count when making a basic
        subscription for one month.
        """
        self.user.make_subscription(1)
        result = self.user.predictions_left
        expected = self.oneMonthSubscription.durationMonths * 60
        self.assertEquals(result, expected)

    def test_customUser_make_subscription_correct_premium_predictions_left_distribution(self):
        """
        Test if customUser make_subscription correctly assigns
        predictions left count when making a premium
        subscription for one month.
        """
        self.user.make_subscription(4)
        result = self.user.predictions_left
        expected = self.premiumOneMonthSubscription.durationMonths * 180
        self.assertEquals(result, expected)

    def test_customUser_add_predictions(self):
        """
        Test if customUser add_predictions adds the desired
        amount of 50 predictions left.
        """
        self.user.add_predictions()
        self.assertEquals(self.user.predictions_left, 50)

    def test_customUser_remove_prediction(self):
        """
        Test if customUser remove_prediction removes the desired
        amount of 1 prediction left.
        """
        self.user.add_predictions()
        self.user.remove_prediction()
        self.assertEquals(self.user.predictions_left, 49)
