from django.db import models, connection
from datetime import datetime

MATCH_TYPE_CHOICES = (
    ('T', 'Match text, ignore color'),
    ('C', 'Match color, ignore text'),
    ('X', 'Match color to text and vice versa'),
)

class Color(models.Model):
    color_name = models.CharField(max_length=40)

    def __unicode__(self):
        return self.color_name

class Game(models.Model):
    match_type = models.CharField(max_length=2, choices=MATCH_TYPE_CHOICES)
    guess_count = models.IntegerField(default=0)
    match_count = models.IntegerField(default=0)
    end_datetime = models.DateTimeField(null=True, blank=True)
    indt = models.DateTimeField(auto_now_add=True)
    updt = models.DateTimeField(auto_now=True)

#    def max_guess_ord(self):
#        cursor = connection.cursor()
#        cursor.execute('select max(guess_ordinal) as max_guess_ord from '
#                + 'colorcon_card where game_id = %s', [self.id])
#        row = cursor.fetchone()
#        return row[0]

class Card(models.Model):
    game = models.ForeignKey(Game)
    color_text = models.ForeignKey(Color, related_name='color_text_set')
    color_display = models.ForeignKey(Color, related_name='color_display_set')
    match_found = models.BooleanField(default=False)
    active_guess = models.BooleanField(default=False)

