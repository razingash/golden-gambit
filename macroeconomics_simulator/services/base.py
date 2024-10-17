from django.core.paginator import Paginator
from stock.utils import CustomException

"""universal functions"""


def get_object(model: object, condition, fields=None): # the best way
    if fields is None:
        fields = []
    obj = model.objects.only(*fields).filter(condition).first()
    if obj is None:
        raise CustomException(f'{model.__name__} object with selected conditions does not exists')
    else:
        return obj


def get_object_or_create(model: object, condition, condtion_create):
    try:
        obj = model.objects.get(condition)
    except model.DoesNotExist:
        obj = model.objects.create(**condtion_create)
        is_created = True
    else:
        is_created = False
    return obj, is_created

def paginate_objects(objects, query_params):
    page = query_params.get('page')
    limit = query_params.get('limit')
    limit = int(limit) if limit is not None else 10
    page = int(page) if page is not None else 1
    paginator = Paginator(objects, limit)

    obj = paginator.get_page(page)
    has_next = obj.has_next()

    return obj, has_next


def get_paginated_objects(model: object, query_params): # later take into account a different limit for each device
    """possible improvement - take into account the passed condition in the filter (when there will be a search by letters)"""
    page = query_params.get('page')
    limit = query_params.get('limit')
    # add condition if needed
    limit = int(limit) if limit is not None else 10
    page = int(page) if page is not None else 1
    objects = model.objects.all().order_by('-id')
    paginator = Paginator(objects, limit)
    obj = paginator.get_page(page)
    has_next = obj.has_next()

    return obj, has_next

