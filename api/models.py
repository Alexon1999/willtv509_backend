from django.db import models

# Create your models here.


class Categorie(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Video(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image_url = models.CharField(max_length=2083, null=True, blank=True)
    video_url = models.CharField(max_length=2083, null=True, blank=True)
    categorie = models.ForeignKey(
        Categorie, on_delete=models.SET_NULL, null=True)
    prix = models.FloatField(default=0)

    def __str__(self):
        return self.title


class MonAbonnement(models.Model):
    subscription_id = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=15, null=True, blank=True)
    product_id = models.CharField(max_length=50, null=True, blank=True)
    stripeCustomerID = models.CharField(max_length=50, null=True, blank=True)


class MonVideo(models.Model):
    payment_intent_id = models.CharField(max_length=50, null=True, blank=True)
    video = models.ForeignKey(
        Video, null=True, blank=True, on_delete=models.SET_NULL)
    payer = models.BooleanField(default=False)
    mode = models.CharField(max_length=20, null=True)

    def __str__(self):
        return self.video.title


class Client(models.Model):
    email = models.EmailField()
    username = models.CharField(max_length=30, null=True, blank=True)
    monAbonnement = models.ForeignKey(
        MonAbonnement, null=True, blank=True, on_delete=models.SET_NULL)
    mesVideos = models.ManyToManyField(MonVideo, blank=True)

    def __str__(self):
        return self.email
