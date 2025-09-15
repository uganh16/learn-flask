from functools import wraps

from flask import current_app, g, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.apis.v1.errors import api_abort, invalid_token, token_missing
from app.models import User


def generate_token(user):
    expiration = 3600
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = s.dumps({'id': user.id})
    return token, expiration


def validate_token(token):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token, max_age=3600)
    except (BadSignature, SignatureExpired):
        return False
    user = User.query.get(data['id'])
    if user is None:
        return False
    g.current_user = user
    return True


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Flask/Werkzeug do not recognize any authentication types other than Basic
        # or Digest, so here we parse the header by hand.
        token_type, token = None, None
        if 'Authorization' in request.headers:
            try:
                token_type, token = request.headers['Authorization'].split(maxsplit=1)
            except ValueError:
                # The Authorization header is either empty or has no token
                pass

        # Flask normally handles OPTIONS requests on its own, but in the case it
        # is configured to forward those to the application, we need to ignore
        # authentication headers and let the request through to avoid unwanted
        # interactions with CORS.
        if request.method != 'OPTIONS':
            if token_type is None or token_type.lower() != 'bearer':
                return api_abort(400, 'The token type must be bearer.')
            if token is None:
                return token_missing()
            if not validate_token(token):
                return invalid_token()

        return f(*args, **kwargs)

    return decorated
