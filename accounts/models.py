from django.db import models


# Create your models here.


class Accounts(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(unique=True, max_length=255)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, max_length=255)
    password = models.CharField(max_length=255)
    active = models.BooleanField()
    type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts"


class Captured(models.Model):
    userid = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    captured = models.FileField()
    file_path = models.FilePathField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "captured"
