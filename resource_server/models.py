from django.db import models

class Resource(models.Model):
    process_id = models.IntegerField() #this is meant to denote a set of steps within a business process
    sequence_number = models.IntegerField() #this is the number within a sequence of steps representing its order in a business process
    description = models.CharField(max_length=200) #this is information about the step
    pub_date = models.DateTimeField("date published")

    def __str__(self):
        return self.process_id, self.sequence_number

    def get_all_steps_in_process(self, process_id):
        return self.process_id == process_id
