from django.db import models
from django.forms import ModelForm

# Create your models here.
class PolsocRequest(models.Model):
    query_name = models.CharField(max_length=255)
    facebook_id = models.CharField(max_length=100)
    facebook_access_token = models.CharField(max_length=255)
    from_date = models.DateField()
    to_date = models.DateField()
    include_comments = models.BooleanField(default=False)
    generate_pdf = models.BooleanField(default=False)
    filename = models.CharField(max_length=100)
    process_state = models.IntegerField(default=0)
    has_been_downloaded = models.BooleanField(default=False)
    
    def __unicode__(self):
        return unicode("fluttershy")

class PolsocRequestForm(ModelForm):
    class Meta:
        model = PolsocRequest
        fields = [
            'query_name',
            'facebook_id',
            'facebook_access_token',
            'from_date',
            'to_date',
            'include_comments'
        ]