from django.db import models
from users.models import User



class Tasks(models.Model):
    creator  = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creator",)
    title = models.CharField(max_length=100)
    description = models.TextField()
    due_date=models.DateField()
    is_done=models.BooleanField(default=False)

