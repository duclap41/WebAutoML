from django.db import models
from django.contrib.auth.models import User

class UserFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='files/')
    photo = models.BinaryField()
    conclusion = models.TextField()
    
    def __str__(self):
        return f"{self.user.username}'s file"