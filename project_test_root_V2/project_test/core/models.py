from django.db import models
import json

class Collection(models.Model):
    name = models.CharField(max_length = 200)

    def __str__(self):
        return self.name
    
class Stack(models.Model):
    content = models.ForeignKey(Collection, on_delete = models.CASCADE)
    text = models.JSONField(max_length = 1000, default="")   

    def __str__(self):
        return json.dumps(self.text)    

