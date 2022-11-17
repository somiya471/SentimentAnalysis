from django.db import models

# Create your models here.
class DataSet(models.Model):
    data_id = models.AutoField
    data_content = models.CharField(max_length=50)
    negative = models.IntegerField()


