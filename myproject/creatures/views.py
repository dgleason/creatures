from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from creatures.models import Creature, Ability, Evolution
from accounts.models import Account
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
import fight, evolve
import urllib2
from django.contrib.auth.decorators import login_required

@login_required
def index(request):

    # delete HPs from session if you retreat to the stable at any point
    try:
        del request.session['creature1']
    except KeyError:
        pass
    try:
        del request.session['creature2']
    except KeyError:
        pass
    try:
        del request.session['creature3']
    except KeyError:
        pass
    try:
        del request.session['enemy']
        print "Deleted enemy health from session"
    except KeyError:
        pass


    account_number = request.user.id
    your_creatures_list = Creature.objects.filter(account=account_number)
    empty_slot = False
    if len(your_creatures_list) < 10:
        empty_slot = True

    #get list of creatures that are in team
    player = Account.objects.get(user=request.user)
    team = player.team.all()

    enemies_list = Creature.objects.filter(account=None)


    context = {'your_creatures_list': your_creatures_list, 'empty_slot': empty_slot, 'team': team, 'enemies_list': enemies_list}
    return render(request, 'creatures/index.html', context)

def cdetail(request, creature_id):
    creature = get_object_or_404(Creature, pk=creature_id)
    evp_left = creature.evp_earned - creature.evp_spent
    evolved_creature = creature.evolve()
    available_evolutions = evolve.allowed_evos(creature)
    affordable_evolutions = []
    for e in available_evolutions:
        if creature.evp_earned - creature.evp_spent > e.cost:
            affordable_evolutions.append(e)

        
    return render(request, 'creatures/cdetail.html', {'creature': evolved_creature, 'available_evolutions': available_evolutions, 'evp_left': evp_left, 'affordable_evolutions': affordable_evolutions})

@login_required
def buy(request, creature_id, evolution_id):
    creature = get_object_or_404(Creature, id=creature_id)
    bought_evo = get_object_or_404(Evolution, id=evolution_id)
    canpay = False
    available_evolutions = evolve.allowed_evos(creature)
    if creature.evp_earned - creature.evp_spent > bought_evo.cost:
        canpay = True
    if canpay == True and bought_evo in available_evolutions:
        creature.evolutions.add(bought_evo)
        creature.evp_earned = creature.evp_earned - bought_evo.cost
        creature.save()
        url = reverse('creatures:creature_detail', args=[creature.id])
        return HttpResponseRedirect(url)
    else:
        return HttpResponse("You can't buy that.")

@login_required
def create(request): 
    return render(request, 'creatures/create.html', {'user': request.user})

@login_required
def make(request):
    body_choice = request.POST['body']
    if body_choice == 'rabbit':
        evos = [get_object_or_404(Evolution, name='Rabbit Form'), get_object_or_404(Evolution, name='Trainer\'s Gift')]
        abil = get_object_or_404(Ability, name='bite')
    elif body_choice == 'lizard':
        evos = [get_object_or_404(Evolution, name='Lizard Form'), get_object_or_404(Evolution, name='Trainer\'s Gift')]
        abil = get_object_or_404(Ability, name='bite')
    else:
        evos = [get_object_or_404(Evolution, name='Scorpion Form'), get_object_or_404(Evolution, name='Trainer\'s Gift')]
        abil = get_object_or_404(Ability, name='sting')
    made_creature = Creature(name=request.POST['name'], ability1=abil)
    made_creature.save()
    made_creature.evolutions.add(*evos) # * unpacks list for add function
    owner = Account.objects.get(user=request.user)
    owner.creatures.add(made_creature)
    return HttpResponseRedirect(reverse('creatures:index'))
# These next two lines are equivalent ways to return the name of creatures owned by the current user.
#    return HttpResponse(Creature.objects.filter(account=request.user.id))
#    return HttpResponse(Account.objects.get(user=request.user).creatures.all())

@login_required
def delete(request, creature_id):
    Creature.objects.filter(id=creature_id).delete()
    return HttpResponseRedirect(reverse('creatures:index'))

@login_required
def cfight(request):
    team = []
    player = Account.objects.get(user=request.user)
    earned = 0
    # Get creature team ids from POST
    if 'team_1' in request.POST or 'team_2' in request.POST or 'team_3' in request.POST:
        player.team.clear()
        team = []
        print "team variable just cleared"
        if 'team_1' in request.POST:
            try:
                team.append(get_object_or_404(Creature, id=request.POST.get("team_1")))
            except urllib2.HTTPError as err:
                if err.code == 404:
                   pass
                else:
                   raise
            except ValueError:
                pass

        if 'team_2' in request.POST:
            try:
                team.append(get_object_or_404(Creature, id=request.POST.get("team_2")))
            except urllib2.HTTPError as err:
                if err.code == 404:
                   pass
                else:
                   raise
            except ValueError:
                pass

        if 'team_3' in request.POST:
            try:
                team.append(get_object_or_404(Creature, id=request.POST.get("team_3")))
            except urllib2.HTTPError as err:
                if err.code == 404:
                   pass
                else:
                   raise
            except ValueError:
                pass


        player.team.add(*team)
        if len(team) <= 0:
            return HttpResponseRedirect(reverse('creatures:index'))
       
    print "adding to pcreatures", player, team
    pcreatures = player.team.all()
    print pcreatures
    # Get enemy out of POST if it is there and save to session
    # Otherwise get it from session or use a default
    if 'enemy' in request.POST:
        enemy = get_object_or_404(Creature, id=request.POST.get("enemy")).evolve()
        request.session['enemy_id'] = enemy.id

    elif request.session.get('enemy_id'):
        print "from session get enemy with id =", request.session.get('enemy_id')
        enemy = get_object_or_404(Creature, id=request.session.get('enemy_id')).evolve()

    else:
        enemy = get_object_or_404(Creature, name="EnemyScorpion").evolve()

    MatchDone = None

    
    # Get healths from session and see if anyone is alive
    total_health_left = 0
    cnum = 1
    for c in pcreatures:
        c = c.evolve()
        c.health_left = 0
        if request.session.get('creature'+str(cnum)):
            c.health_left = request.session.get('creature'+str(cnum))["health_left"]
            print c.name, "had health in session:", c.health_left
        cnum = cnum + 1
        total_health_left = total_health_left + max(c.health_left, 0)


    enemy.health_left = 0
    if request.session.get('enemy'):
        enemy.health_left = request.session.get('enemy')["health_left"]
    print "total_health before combat:", total_health_left



    # if both teams aren't alive in a session, start a fresh one
    if not total_health_left > 0 or not enemy.health_left > 0:
        print 'start new session'
        for cnum in range(0, 3):
            try:
                del request.session['creature'+str(cnum)]
            except KeyError:
                pass


        cnum = 1
        for c in pcreatures:
            c.health_left = c.health
            request.session['creature'+str(cnum)] = {'health_left': c.health_left}
            cnum += 1

        total_health_left = 0 #recalculate t_h_l for new session
        for c in pcreatures:
            total_health_left = total_health_left + max(c.health_left, 0)


        enemy.health_left = enemy.health
        request.session['enemy'] = {'health_left': enemy.health_left}      


    # choose the current combatant
    current = fight.current(pcreatures)


    
    # Use player's chosen attack
    result = None
    if request.method=='POST':
        if not 'team1' in request.POST:
            if 'ability1' in request.POST:
                result = fight.combat(current, current.ability1, enemy)
            elif 'ability2' in request.POST:
                result = fight.combat(current, current.ability2, enemy)
            elif 'ability3' in request.POST:
                result = fight.combat(current, current.ability3, enemy)

            # After attack, save new health_left values to session
            # This is dumb, I can't name session value after the creature
            # because I won't know how to clear them if user changes the team.
            # But since names are generic, I can't update just one creature.
            cnum = 1
            total_health_left = 0
            for c in pcreatures:
                total_health_left = total_health_left + max(c.health_left, 0)
                request.session['creature'+str(cnum)] = {'health_left': c.health_left}
                print "updated HP after attack:", c.name, cnum, request.session['creature'+str(cnum)]
                cnum = cnum + 1


            request.session['enemy'] = {'health_left': enemy.health_left}




    # If one team is dead, end fight
    if enemy.health_left <= 0:
        MatchDone = 'Victory'
    elif total_health_left <= 0:
        MatchDone = 'Defeat'
    print MatchDone



    # if a pcreature died, and replacement steps in, mention it
    if current.health_left <= 0:
        if fight.current(pcreatures) != None:
            result[1] =  ' '.join([result[1], fight.current(pcreatures).name, 'steps up to fight.'])
    
    # update the current combatant in case one died
    current = fight.current(pcreatures)

    # If the match ended in victory, award some Evolution Points
    if MatchDone == 'Victory':
        # Reward more points for strong enemies, less for strong player teams
        player_value = 15
        for c in pcreatures:
            player_value = (player_value + c.evp_spent)
        
        enemy_value = 0
        for e in enemy.evolutions.all():
            enemy_value = enemy_value + e.cost
        

        earned = int((enemy_value - player_value)/3)+1
        for c in pcreatures:
            c.evp_earned = c.evp_earned + earned
            c.save()
            
        print "Enemy Value:", enemy_value, "-- Player Value: ", player_value
        print "All creatures earned EVP! Amount: ", earned

  
    context = {'player': player, 'pcreatures': pcreatures, 'current': current, 'enemy': enemy, 'result': result, 'matchdone': MatchDone, 'earned': earned}
    return render(request, 'creatures/fight.html', context)


