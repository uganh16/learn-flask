from flask import current_app, g, jsonify, request, url_for
from flask.views import MethodView

from app.apis.v1.auth import auth_required, generate_token
from app.apis.v1.errors import ValidationError, api_abort
from app.apis.v1.schemas import item_schema, items_schema, user_schema
from app.extensions import db
from app.models import Item, User


def get_item_body():
    data = request.get_json()
    body = data.get('body')
    if body is None or str(body).strip() == '':
        raise ValidationError('The item body was empty or invalid.')
    return body


class IndexAPI(MethodView):
    def get(self):
        return jsonify(
            api_version="1.0",
        )


class AuthTokenAPI(MethodView):
    def post(self):
        grant_type = request.form.get('grant_type')
        username = request.form.get('username')
        password = request.form.get('password')

        if grant_type is None or grant_type.lower() != 'password':
            return api_abort(code=400, message='The grant type must be password.')

        user = User.query.filter_by(username=username).first()
        if user is None or not user.validate_password(password):
            return api_abort(code=400, message='Invalid username or password.')

        token, expiration = generate_token(user)

        response = jsonify(
            access_token=token,
            token_type='Bearer',
            expires_in=expiration
        )
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Pragma'] = 'no-cache'
        return response


class UserAPI(MethodView):
    decorators = [auth_required]

    def get(self):
        return jsonify(user_schema(g.current_user))


class ItemAPI(MethodView):
    decorators = [auth_required]

    def get(self, item_id):
        '''Get item.'''
        item = Item.query.get_or_404(item_id)
        if g.current_user != item.author:
            return api_abort(403)
        return jsonify(item_schema(item))

    def put(self, item_id):
        '''Edit item.'''
        item = Item.query.get_or_404(item_id)
        if g.current_user != item.author:
            return api_abort(403)
        item.body = get_item_body()
        db.session.commit()
        return '', 204

    def patch(self, item_id):
        '''Toggle item.'''
        item = Item.query.get_or_404(item_id)
        if g.current_user != item.author:
            return api_abort(403)
        item.done = not item.done
        db.session.commit()
        return '', 204

    def delete(self, item_id):
        '''Toggle item.'''
        item = Item.query.get_or_404(item_id)
        if g.current_user != item.author:
            return api_abort(403)
        db.session.delete(item)
        db.session.commit()
        return '', 204


class ItemsAPI(MethodView):
    decorators = [auth_required]

    def get(self):
        '''Get all items of the current user.'''
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['TODOISM_ITEM_PER_PAGE']
        pagination = Item.query.with_parent(g.current_user).paginate(page=page, per_page=per_page)
        return jsonify(items_schema('.items', pagination))

    def post(self):
        '''Create new item.'''
        body = get_item_body()
        item = Item(body=body, author=g.current_user)
        db.session.add(item)
        db.session.commit()
        response = jsonify(item_schema(item))
        response.status_code = 201
        response.headers['Location'] = url_for('.item', item_id=item.id, _external=True)
        return response


class ActiveItemsAPI(MethodView):
    decorators = [auth_required]

    def get(self):
        '''Get active items of the current user.'''
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['TODOISM_ITEM_PER_PAGE']
        pagination = Item.query.with_parent(g.current_user).filter_by(done=False).paginate(page=page, per_page=per_page)
        return jsonify(items_schema('.active_items', pagination))


class CompletedItemsAPI(MethodView):
    decorators = [auth_required]

    def get(self):
        '''Get completed items of the current user.'''
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['TODOISM_ITEM_PER_PAGE']
        pagination = Item.query.with_parent(g.current_user).filter_by(done=True).paginate(page=page, per_page=per_page)
        return jsonify(items_schema('.completed_items', pagination))

    def delete(self):
        '''Clear current user's completed items.'''
        Item.query.with_parent(g.current_user).filter_by(done=True).delete()
        db.session.commit()
        return '', 204
