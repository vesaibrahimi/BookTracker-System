from django.db import models
from django.contrib.auth.models import User

class Book(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    price = models.CharField(max_length=100)
    stock = models.CharField(max_length=100)
    description = models.TextField()
    upc = models.CharField(max_length=100)
    num_reviews = models.IntegerField(default=0)
    created_manually = models.BooleanField(default=False)  # to track if added manually or scraped

    def __str__(self):
        return self.title

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    scraping_pages = models.CharField(max_length=100, help_text="Pages that user can scrape")
    
    def __str__(self):
        return self.user.username
