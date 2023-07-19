from django.contrib.auth.models import AbstractUser
from django.db import models
import json

class User(AbstractUser):
    def __str__(self):
        return self.username

class FavouriteList(models.Model):
    username = models.CharField(max_length=150)
    def __str__(self):
        return self.username

class Word(models.Model):
    name = models.CharField(max_length=150)
    defn = models.TextField()
    audio_link = models.CharField(max_length=150, blank=True, null=True)
    #favourite_list = models.ForeignKey(FavouriteList, on_delete=models.CASCADE,related_name="words")
    favourite_list = models.ManyToManyField(FavouriteList, related_name="words")
    mimgs = models.TextField(blank=True, null=True)     

    def __str__(self):
        return self.name

    def serialize(self):
        return {
            "name": self.name,
            "defn": self.defn,
            "audio_link": self.audio_link,
        }

    def set_mimgs(self, link):
        self.mimgs = json.dumps(link)

    def get_mimgs(self):
        #print(f">>>self.mimgs: {self.mimgs}")
        return json.loads(self.mimgs)

class Phrase(models.Model):
    name = models.CharField(max_length=150)
    audio_link = models.CharField(max_length=150)
    word = models.ForeignKey(Word, on_delete=models.CASCADE,related_name="phrases")

    def serialize(self):
        return {
            "name": self.name,
            "audio_link": self.audio_link,
        }