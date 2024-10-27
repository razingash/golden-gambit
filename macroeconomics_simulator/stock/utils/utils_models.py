from datetime import timedelta

from django.db import models
from django.utils import timezone
"""Choices, model related functions"""

class CompanyTypes(models.IntegerChoices):
    FARM = 1, 'farm' # 1x
    FISH_FARM = 2, 'fish farm'
    MINE = 3, 'mine'
    ORE_MINE = 4, 'ore mine'
    QUARRY = 5, 'quarry'
    SAWMILL = 6, 'sawmill'
    PLANTATION = 7, 'plantation'
    FOOD_FACTORY = 8, 'food factory' # x2
    DEEP_SEA_FISHING_ENTERPRISE = 9, 'deep sea fishing enterprise'
    CHEMICAL_PLANT = 10, 'chemical plant'
    METALLBURGICAL_PLANT = 11, 'metallburgical plant'
    BRICK_FACTORY = 12, 'brick factory'
    GLASS_FACTORY = 13, 'glass factory'
    WOOD_PROCESSING_PLANT = 14, 'wood processing plant'
    TEXTILE_FACTORY = 15, 'textile factory'
    PHARMACEUTICAL_COMPANY = 16, 'pharmaceutical company' # x4
    MICROELECTRONICS_PRODUCTION_PLANT = 17, 'microelectonics production plant'
    ENGINEERING_PLANT = 18, 'engineering plant'
    FURNITURE_FACTORY = 19, 'furniture factory'
    CLOTHING_FACTORY = 20, 'clothing factory'
    OIL_COMPANY = 21, 'oil company' # x6
    OIL_REFINING_COMPANY = 22, 'oil refining company' # 8x
    DEFENSE_INDUSTRY = 23, 'defense industry'
    CONSTRUCTION_COMPANY = 24, 'construction company'
    CLOTHING_FACTORY_2 = 25, 'clothing factory 2'


class ProductTypes(models.IntegerChoices):
    UNPROCESSED_FOOD = 1, 'unprocessed food' # 1x | 2x
    MINERALS = 2, 'minerals'
    BASE_METALS = 3, 'base metals'
    SLATE = 4, 'slate'
    LIMESTONE = 5, 'limestone'
    CLAY = 6, 'clay'
    WOOD = 7, 'wood'
    # 2x
    PROCESSED_FOOD = 8, 'processed food'
    CHEMICALS = 9, 'chemicals'
    PROCESSED_METALS = 10, 'processed metals'
    BUILDING_MATERIALS = 11, 'building materials' # x8
    PROCESSED_WOOD = 12, 'processed wood'
    TEXTILE = 13, 'textile'
    # 4x
    MEDICINES = 14, 'medicines'
    MICROELECTRONICS = 15, 'microelectronics'
    MECHANICAL_PARTS = 16, 'mechanical parts'
    FURNITURES = 17, 'furnitures'
    CLOTHING = 18, 'clothing'
    OIL = 19, 'oil' # x6
    # x8
    SPECIAL_CLOTHING = 20, 'special clothing'
    WEAPONS = 21, 'weapons'
    FUEL = 22, 'fuel'
    CONSTRUCTION_RAW_MATERIALS = 23, 'construction raw materials'


class SharesTypes(models.IntegerChoices):
    ORDINARY = 1, 'ordinary'
    PREFERRED = 2, 'preferred'


class EventStates(models.IntegerChoices):
    """You can make sure that the duration of events isn't random, but this is unnecessary"""
    INACTIVE = 1, 'inactive' # default state
    BEGINNING = 2, 'beginning' # weak price spike lasting 1-3 days
    CULMINATION = 3, 'culmination' # depends on the event
    CONSEQUENCES = 4, 'consequences' # average price spike lasting 3-6 days


class EventTypes(models.IntegerChoices):
    CROP_FAILURE = 1, 'crop failure'
    RICH_HARVEST = 2, 'rich harvest'
    EARTHQUAKE = 3, 'earthquake'
    FLOOD = 4, 'flood'
    EXTREME_HEAT = 5, 'extreme heat'
    DROUGHT = 6, 'drought'
    FOREST_FIRES = 7, 'forest fires'
    EPIDEMIC = 8, 'epidemic'
    PANDEMIC_OUTBREAK = 9, 'pandemic outbreak'
    WORKERS_STRIKES = 10, 'workers’ strikes'
    PROTESTS = 11, 'protests'
    CIVIL_WAR = 12, 'civil war'
    WAR = 13, 'war'


def right_of_purchase_for_owners(): # shares are available only to the head of a company | mb owner also
    return timezone.now() + timedelta(hours=1)

def right_of_purchase_for_shareholders(): # shares are available only to the shareholders, after 6 hours to everyone
    return timezone.now() + timedelta(hours=6)

def remove_company_recipes_duplicates(data):
    seen = set()
    unique_data = []

    for entry in data:
        entry_tuple = (
            entry['company_type'],
            tuple((ingredient['type'], ingredient['amount']) for ingredient in entry['ingredients'])
        )

        if entry_tuple not in seen:
            unique_data.append(entry)
            seen.add(entry_tuple)

    return unique_data
