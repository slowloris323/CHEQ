from django.db import models

class ResourceUriCheqMapping(models.Model):
    resource_uri = models.URLField()
    CHEQ = models.JSONField()

    def __str__(self):
        return self.resource_uri, self.CHEQ

    def get_cheq(self, resource_uri):
        return self.resource_uri == resource_uri