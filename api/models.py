from django.db import models


# Create your models here.
class AudioFile(models.Model):
    file = models.FileField(upload_to="audios/")
