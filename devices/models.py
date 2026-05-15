from django.db import models


class Device(models.Model):
    USAGE_CHOICES = [
        ('gaming', 'Gaming'),
        ('student', 'Student'),
        ('camera', 'Camera'),
        ('business', 'Business'),
        ('daily', 'Daily Use'),
    ]

    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=100)

    price = models.IntegerField(default=0)

    ram = models.CharField(max_length=50, blank=True, null=True)
    storage = models.CharField(max_length=50, blank=True, null=True)
    battery = models.CharField(max_length=100, blank=True, null=True)
    processor = models.CharField(max_length=255, blank=True, null=True)
    camera = models.CharField(max_length=255, blank=True, null=True)
    display = models.CharField(max_length=255, blank=True, null=True)

    image_url = models.URLField(blank=True, null=True)
    source_url = models.URLField(blank=True, null=True)
    buy_link = models.URLField(blank=True, null=True)

    usage_tag = models.CharField(
        max_length=50,
        choices=USAGE_CHOICES,
        default='daily'
    )

    ai_score = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Favorite(models.Model):

    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE
    )

    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE
    )

    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.device.name}"