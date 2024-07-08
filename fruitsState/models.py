from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class FruitCount(models.Model):
    unknown = models.IntegerField(default=0) 
    appleBad =models.IntegerField(default=0) 
    bananaBad=models.IntegerField(default=0) 
    orangeBad=models.IntegerField(default=0) 
    pomegranateBad=models.IntegerField(default=0) 
    appleGood=models.IntegerField(default=0) 
    bananaGood=models.IntegerField(default=0) 
    orangeGood=models.IntegerField(default=0) 
    pomegranateGood=models.IntegerField(default=0) 


class ImageModel(models.Model):
    image = models.ImageField(upload_to='fruitsImages/')
    imagesDetected = models.ImageField(upload_to='fruitsDetectedImages/',null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True,  null=True, blank=True)
    fruitsState = models.CharField(max_length=500, blank=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    fruitCount_id = models.ForeignKey(FruitCount, on_delete=models.CASCADE, null=True, blank=True)
    unknown = models.IntegerField(default=0) 
    bad_apple =models.IntegerField(default=0) 
    bad_banana=models.IntegerField(default=0) 
    bad_orange=models.IntegerField(default=0) 
    bad_pomegranate=models.IntegerField(default=0) 
    good_apple=models.IntegerField(default=0) 
    good_banana=models.IntegerField(default=0) 
    good_orange=models.IntegerField(default=0) 
    good_pomegranate=models.IntegerField(default=0) 
    

    def __str__(self):
        return self.fruitsState
