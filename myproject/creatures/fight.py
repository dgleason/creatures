# fight.py
from creatures.models import Creature, Ability, Evolution
from random import randint


def current(pcreatures):
    for c in pcreatures:
        if c.health_left > 0:
            return c
    return None

def UseAbility(attacker, ability, target):
    dodge = 0
    crit = 0
    if ability.damage_type == 'Physical':
        defense = target.armor
    elif ability.damage_type == 'Elemental':
        defense = target.constitution
    if randint(1,5) == 5:
        dodge = target.dodge - attacker.accuracy
    if randint(1,5) == 5:
        crit = attacker.crit_bonus
    raw_damage = attacker.atk_power + crit
    damage_reduced = defense + dodge
    damage_done = max((raw_damage - damage_reduced), 0)
    target.health_left = target.health_left - damage_done

    # Building combat strings
    # "Silversing claws at StrayDog."
    str_1 = ' '.join([attacker.name, ability.combat_string, target.name])+'. '

    if crit > 0 and damage_done > 0:
        # It's a critical hit!
        str_2 = "It's a <strong>critical hit</strong>! "
    else:
        # blank
        str_2 = ''

    if damage_done > 0 and dodge > 0:
        # StrayDog dodges part of the attack, taking only 3 damage.
        str_3 = ' '.join([target.name, '<strong>dodges</strong> part of the blow, taking only', str(damage_done), 'damage. '])
    elif dodge > 0 and damage_done == 0:
        # StrayDog dodges the attack completely!
        str_3 = ' '.join([target.name, '<strong>dodges</strong> out of the way! '])
    elif dodge == 0:
        # StrayDog takes 5 damage.
        str_3 = ' '.join([target.name, 'takes', str(damage_done), 'damage. '])

    if target.health_left <= 0:
        # The blow is fatal!
        str_4 = "The blow is <strong>fatal</strong>!"
    elif target.health_left > 0:
        # blank
        str_4 = ''

    strike = str_1 + str_2 + str_3 + str_4
    return strike

def combat(current, pability, enemy):
    eability = enemy.ability1
    if current.health_left > 0:
        cstrike = UseAbility(current, pability, enemy)
    if enemy.health_left > 0:
        estrike = UseAbility(enemy, eability, current)
    else:
        estrike = enemy.name+" is dead!"
    result = [cstrike, estrike]
    return result





