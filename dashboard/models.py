from django.db import models
from accounts.models import Accounts


# Create your models here.

class Attendance(models.Model):
    userid = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    marked_at = models.DateTimeField(blank=True, null=True)
    marked_out = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance'
