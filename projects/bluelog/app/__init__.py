import click
from flask import Flask, render_template

from app.extensions import bootstrap, db
from app.models import Admin, Category, Comment, Post


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    register_shell_context(app)
    register_template_context(app)
    register_commands(app)

    return app


def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)


def register_blueprints(app):
    from app.blueprints import admin, auth, blog

    app.register_blueprint(blog.bp)
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(admin.bp, url_prefix='/admin')


def register_errorhandlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('error.html', status_code=400, description='Bad Request'), 400

    @app.errorhandler(404)
    def not_found(e):
        return render_template('error.html', status_code=404, description='Page Not Found'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error.html', status_code=500, description='Internal Server Error'), 500


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, Admin=Admin, Category=Category, Comment=Comment, Post=Post)


def register_template_context(app):
    @app.context_processor
    def make_template_context():
        admin = Admin.query.first()
        categories = Category.query.order_by(Category.name).all()
        return dict(admin=admin, categories=categories)


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def init_db(drop):
        '''Initialize the database.'''
        if drop:
            click.confirm(
                'This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    @click.option('--category', default=10, help='Quantity of categories, default is 10.')
    def forge(category):
        '''Generate fake data.'''
        from app.fakes import fake_admin, fake_categories

        db.drop_all()
        db.create_all()

        click.echo('Generating the administrator...')
        fake_admin()

        click.echo('Generating {0} categories...'.format(category))
        fake_categories(category)

        click.echo('Done.')
