import click
from flask import Flask, render_template
from flask_login import current_user

from app.blueprints import auth, home, todo
from app.extensions import csrf, db, login_manager
from app.models import Item



def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    register_template_context(app)
    register_commands(app)

    return app


def register_extensions(app):
    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app):
    app.register_blueprint(auth.bp)
    app.register_blueprint(home.bp)
    app.register_blueprint(todo.bp)


def register_errorhandlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('error.html', code=400, info='Bad Request'), 400 # @todo _

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('error.html', code=403, info='Forbidden'), 403 # @todo _

    @app.errorhandler(404)
    def not_found(e):
        return render_template('error.html', code=404, info='Page Not Found'), 404 # @todo _

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error.html', code=500, info='Server Error'), 500 # @todo _


def register_template_context(app):
    @app.context_processor
    def make_template_context():
        if current_user.is_authenticated:
            active_items = Item.query.with_parent(current_user).filter_by(done=False).count()
        else:
            active_items = None
        return dict(active_items=active_items)


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def init_db(drop):
        '''Initialize the database.'''
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')
