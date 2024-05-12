from django.db import models

class User(models.Model):
    fullname = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phonenumber = models.CharField(max_length=100)
    dateofbirth = models.DateField()
    # Các trường khác liên quan đến thông tin người dùng
    def __str__(self):
        return str([self.fullname, self.email, self.phonenumber, self.dateofbirth])


class UserFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    csvfile = models.TextField()
    photo = models.BinaryField()
    conclusion = models.TextField()
