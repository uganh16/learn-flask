from faker import Faker
from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Item, User


bp = Blueprint('auth', __name__)

fake = Faker()


@bp.route('/register')
def register():
    while True:
        # generate a random account for demo use
        username = fake.user_name()
        password = fake.word()
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        # make sure the generated username was not in database
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        else:
            break

    # @todo _
    item1 = Item(body='Witness something truly majestic', author=user)
    item2 = Item(body='Help a complete stranger', author=user)
    item3 = Item(body='Drive a motorcycle on the Great Wall of China', author=user)
    item4 = Item(body='Sit on the Great Egyptian Pyramids', done=True, author=user)

    db.session.add_all([item1, item2, item3, item4])
    db.session.commit()

    # @todo _
    return jsonify(username=username, password=password, message='Generate success.')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data['username']
        password = data['password']

        user = User.query.filter_by(username=username).first()

        if user is not None and user.validate_password(password):
            login_user(user)
            return jsonify(message='Login success.') # @todo _

        return jsonify(message='Invalid username or password.'), 400 # @todo _

    if current_user.is_authenticated:
        return redirect(url_for('todo.app'))

    return render_template('_login.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify(message='Logout success.') # @todo _
