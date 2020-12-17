from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class CustomAccountManager(BaseUserManager):
    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(email=self.normalize_email(email), **extra_fields)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class Subscription(models.Model):
    subscriptionType = models.CharField(max_length=20)
    durationMonths = models.IntegerField(default=1)
    name = models.CharField(max_length=20, default=None)

    subscriptionTypes = models.Manager()

    def __str__(self):
        return self.subscriptionType


class ApartmentType(models.Model):
    apartmentType = models.CharField(max_length=20)

    def __str__(self):
        return self.apartmentType


class ConstructionType(models.Model):
    constructionType = models.CharField(max_length=20)

    def __str__(self):
        return self.constructionType


class District(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    subscriptionStartDate = models.DateField(blank=True, null=True)
    subscriptionEndDate = models.DateField(blank=True, null=True)
    subscription = models.ForeignKey(
        Subscription, on_delete=models.PROTECT, related_name="+", blank=True, null=True
    )
    is_staff = models.BooleanField(default=False)
    predictionsLeft = models.IntegerField(default=0)

    objects = CustomAccountManager()

    USERNAME_FIELD = "email"

    @property
    def predictions_left(self):
        return self.predictionsLeft

    @predictions_left.setter
    def predictions_left(self, value):
        self.predictionsLeft = value

    def has_subscription(self):
        now_time = timezone.now()
        if not self.subscription or self.subscriptionEndDate < now_time.date():
            # Make subscription and its date None if it has ended
            self.subscriptionStartDate = None
            self.subscriptionEndDate = None
            self.subscription = None
            self.save()
            return False
        return True

    def has_predictions_left(self):
        return True if self.predictions_left > 0 else False

    def make_subscription(self, subsId):
        self.subscription = Subscription.subscriptionTypes.get(id=subsId)
        self.subscriptionStartDate = timezone.now()

        # Check if user has an active subscription
        if self.subscriptionEndDate is not None:
            self.subscriptionEndDate = self.subscriptionEndDate + relativedelta(months=self.subscription.durationMonths)
        else:
            self.subscriptionEndDate = self.subscriptionStartDate + relativedelta(
                months=self.subscription.durationMonths)

        # Basic subscriptions have ids 1, 2 and 3
        if 1 <= self.subscription.id <= 3:
            self.predictions_left = self.predictions_left + (self.subscription.durationMonths * 60)
        # Premium subscriptions
        else:
            self.predictions_left = self.predictions_left + (self.subscription.durationMonths * 180)

        self.save()

    def add_predictions(self):
        self.predictions_left = self.predictions_left + 50
        self.save()
    
    def remove_prediction(self):
        self.predictions_left = self.predictions_left - 1
        self.save()


class History(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="+")
    apartmentType = models.ForeignKey(ApartmentType, on_delete=models.PROTECT, related_name="+")
    constructionType = models.ForeignKey(ConstructionType, on_delete=models.PROTECT, related_name="+")
    district = models.ForeignKey(District, on_delete=models.PROTECT, related_name="+")
    pricePrediction = models.PositiveIntegerField(validators=[MinValueValidator(5000)])
    datePrediction = models.DateTimeField(auto_now_add=True)
    squareMeters = models.PositiveIntegerField(validators=[MinValueValidator(10)])
    priceSQM = models.PositiveIntegerField(validators=[MinValueValidator(10)])
    currency = models.CharField(max_length=3)
    year = models.PositiveIntegerField(validators=[MinValueValidator(1880), MaxValueValidator(2030)])
    floor = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    gas = models.BooleanField(default=False)
    heating = models.BooleanField(default=False)
    furnished = models.BooleanField(default=False)
    entranceControl = models.BooleanField(default=False)
    security = models.BooleanField(default=False)
    passageway = models.BooleanField(default=False)


class ContactMessage(models.Model):
    fullname = models.CharField(max_length=40)
    email = models.EmailField(verbose_name="email", max_length=60, unique=False)
    title = models.CharField(max_length=30)
    message = models.TextField()

    def __str__(self):
        return self.title
