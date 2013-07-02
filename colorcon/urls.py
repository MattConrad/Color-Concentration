from django.conf.urls.defaults import *

urlpatterns = patterns('ccsite.colorcon.views',
    (r'^$', 'current_game'),
    (r'^create_new_game/(?P<match_type>C|T|X)/$', 'create_new_game'),
    (r'^(?P<new_card_id>\d+)/$', 'guess'),
    (r'^failed_match/$', 'failed_match'),
    (r'^won_game/$', 'won_game'),
    (r'^clear_failed_matches/$', 'clear_failed_matches'),
    (r'^init_colors/$', 'init_colors'),
)    
        
