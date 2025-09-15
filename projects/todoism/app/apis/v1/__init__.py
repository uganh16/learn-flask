from flask import Blueprint
from flask_cors import CORS

from app.apis.v1.errors import ValidationError, api_abort
from app.apis.v1.resources import (
    ActiveItemsAPI,
    AuthTokenAPI,
    CompletedItemsAPI,
    IndexAPI,
    ItemAPI,
    ItemsAPI,
    UserAPI,
)


bp = Blueprint('api_v1', __name__)

CORS(bp)


bp.add_url_rule('/', view_func=IndexAPI.as_view('index'), methods=['GET'])
bp.add_url_rule('/oauth/token', view_func=AuthTokenAPI.as_view('token'), methods=['POST'])
bp.add_url_rule('/user', view_func=UserAPI.as_view('user'), methods=['GET'])
bp.add_url_rule('/user/items/<int:item_id>', view_func=ItemAPI.as_view('item'), methods=['GET', 'PUT', 'PATCH', 'DELETE'])
bp.add_url_rule('/user/items', view_func=ItemsAPI.as_view('items'), methods=['GET', 'POST'])
bp.add_url_rule('/user/items/active', view_func=ActiveItemsAPI.as_view('active_items'), methods=['GET'])
bp.add_url_rule('/user/items/completed', view_func=CompletedItemsAPI.as_view('completed_items'), methods=['GET', 'DELETE'])

@bp.errorhandler(ValidationError)
def validation_error(e):
    return api_abort(400, e.args[0])
