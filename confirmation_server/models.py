from django.db import models

class Trigger(models.Model):
    resource_uri = models.URLField()
    confirmation_uri = models.URLField()

    def __str__(self):
        return self.resource_uri
