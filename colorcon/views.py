from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from ccsite.colorcon.models import Game, Color, Card
from datetime import datetime
import random

def clear_failed_matches(request):
    game_id = request.session['game_id']
    game = Game.objects.get(pk=game_id)
    # i suppose we only should have 2 objects here, so no custom SQL.
    guesses = Card.objects.filter(game=game.id, active_guess=True)
    for card in guesses:
        card.active_guess = False
        card.save()
    return HttpResponseRedirect(reverse('ccsite.colorcon.views.current_game'))

def create_new_game(request, match_type):
    new_game = Game()
    new_game.match_type = match_type 
    new_game.save()
    request.session['game_id'] = new_game.id
    random.seed()
    color_ids = [c.id for c in Color.objects.all()]
    color_pairs = get_color_pairs(color_ids)
    color_pairs.extend(get_color_pairs(color_ids))
    random.shuffle(color_pairs)
    for t, d in color_pairs:
        card = Card()
        card.game = new_game
        card.color_text_id = t
        card.color_display_id = d
        card.save()
    return HttpResponseRedirect(reverse('ccsite.colorcon.views.current_game'))

def current_game(request):
    game_id = request.session.get('game_id', None)
    try: 
        game = Game.objects.get(pk=game_id)
    except Game.DoesNotExist:
        game = None

    if game:
        return render_to_response('index.html', 
                {'cards': game.card_set.all(), 'game': game} )
    else:
        return render_to_response('select_new_game.html')

def failed_match(request):
    game_id = request.session['game_id'] 
    game = Game.objects.get(pk=game_id)
    return render_to_response('index.html', 
            {'cards': game.card_set.all(), 'game': game, 'special': 'failed_match'} )

def get_color_pairs(cids):
    cidsa, cidsb = cids[:], cids[:]
    random.shuffle(cidsa)
    random.shuffle(cidsb)
    cpairs = []
    for i in range(len(cidsa)): 
        if cidsa[-1] != cidsb[-1]:
            cpairs.append( (cidsa.pop(), cidsb.pop()) )
        else:
            cpairs.append( (cidsa.pop(), cidsb.pop(0)) )
    return cpairs

def guess(request, new_card_id):
    new_card = Card.objects.get(id=new_card_id)
    game = new_card.game
    guesses = Card.objects.filter(game=game.id, active_guess=True)
    return_view = 'current_game' 
    # first-card turnover, or 2nd card to compare for match?
    if len(guesses) == 0:
        new_card.active_guess = True
        new_card.save()
    elif len(guesses) == 1:
        if game.match_type == 'C':
            new_card_color = new_card.color_display
            prior_card_color = guesses[0].color_display
        elif game.match_type == 'T':
            new_card_color = new_card.color_text
            prior_card_color = guesses[0].color_text
        elif game.match_type == 'X':
            new_card_color = new_card.color_display
            prior_card_color = guesses[0].color_text
        else:
            raise ValueError('Invalid game match type.')

        print new_card_color
        print prior_card_color

        # if it's a match, mark & return for new first-card turnover.
        # else, return special so can show bad-guess-disabled-input
        if (new_card_color == prior_card_color):
            guesses[0].active_guess = False  # impt, don't forget!
            guesses[0].match_found = True
            new_card.match_found = True
            guesses[0].save()
            new_card.save()
            game.match_count += 2
            if game.match_count >= game.card_set.count():
                game.end_datetime = datetime.now()
                return_view = 'won_game'
        else:
            new_card.active_guess = True
            new_card.save()
            return_view = 'failed_match'
        
    game.guess_count += 1
    game.save()
    return HttpResponseRedirect(reverse('ccsite.colorcon.views.%s' % return_view))

def init_colors(request):
    for color_name in ['aqua', 'yellow', 'green', 'purple', 'orange', 'white',
            'gray', 'blue', 'red', 'pink']:
        new_color = Color()
        new_color.color_name = color_name
        new_color.save()
    return HttpResponseRedirect(reverse('ccsite.colorcon.views.current_game'))

def won_game(request):
    game_id = request.session['game_id']
    game = Game.objects.get(pk=game_id)
    request.session.flush()
    return render_to_response('index.html', 
            {'cards': game.card_set.all(), 'game': game, 'special': 'won_game'} )
