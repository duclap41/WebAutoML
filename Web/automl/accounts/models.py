from django.db import models
from django.contrib.auth.models import User

class UserFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data_file = models.FileField(upload_to='save_files/')
    best_model = models.TextField()
    best_result = models.TextField()
    last_target = models.TextField()
    last_features = models.TextField()

    def __str__(self):
        return f"{self.user}'s file"