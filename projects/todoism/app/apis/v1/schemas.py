from flask import url_for

from app.models import Item


def user_schema(user):
    return {
        'id': user.id,
        'self': url_for('.user', _external=True),
        'kind': 'User',
        'username': user.username,
        'all_items_url': url_for('.items', _external=True),
        'active_items_url': url_for('.active_items', _external=True),
        'completed_items_url': url_for('.completed_items', _external=True),
        'all_item_count': len(user.items),
        'active_item_count': Item.query.with_parent(user).filter_by(done=False).count(),
        'completed_item_count': Item.query.with_parent(user).filter_by(done=True).count(),
    }


def item_schema(item):
    return {
        'id': item.id,
        'self': url_for('.item', item_id=item.id, _external=True),
        'kind': 'Item',
        'body': item.body,
        'done': item.done,
        'author': {
            'url': url_for('.user', _external=True),
            'username': item.author.username,
            'kind': 'User',
        },
    }


def items_schema(endpoint, pagination):
    return {
        'self': url_for(endpoint, page=pagination.page, _external=True),
        'kind': 'ItemCollection',
        'items': [item_schema(item) for item in pagination.items],
        'prev': url_for(endpoint, page=pagination.page-1, _external=True) if pagination.has_prev else None,
        'next': url_for(endpoint, page=pagination.page+1, _external=True) if pagination.has_next else None,
        'last': url_for(endpoint, page=pagination.pages, _external=True),
        'first': url_for(endpoint, page=1, _external=True),
        'total': pagination.total,
    }
