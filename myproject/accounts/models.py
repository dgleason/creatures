from django.db import models
from creatures.models import Creature
from django.contrib.auth.models import User

class Account(models.Model):
    user = models.OneToOneField(User)
    creatures = models.ManyToManyField(Creature, blank=True)
    team = models.ManyToManyField(Creature, blank=True, null=True, related_name='team')
    
    def __unicode__(self):
        return self.user.username
