import click
from flask import Flask, render_template

from app.extensions import bootstrap, db, moment
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
    moment.init_app(app)


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
    @click.option('--username', prompt=True, help='The username used to login.')
    @click.option('--password', prompt=True, help='The password used to login.', hide_input=True, confirmation_prompt=True)
    def init(username, password):
        '''Building Bluelog, just for you.'''

        click.echo('Initializing the database...')
        db.create_all()

        admin = Admin.query.first()
        if admin is not None:
            click.echo('The administrator already exists, updating...')
            admin.username = username
            admin.set_password(password)
        else:
            click.echo('Creating the temporary administrator account...')
            admin = Admin(
                username=username,
                blog_title='Bluelog',
                blog_sub_title="No, I'm the real thing.",
                name='Admin',
                about='Anything about you.',
            )
            admin.set_password(password)
            db.session.add(admin)

        category = Category.query.first()
        if category is None:
            click.echo('Creating the default category...')
            category = Category(name='Default')
            db.session.add(category)

        db.session.commit()
        click.echo('Done.')

    @app.cli.command()
    @click.option('--category', default=10, help='Quantity of categories, default is 10.')
    @click.option('--post', default=50, help='Quantity of posts, default is 50.')
    @click.option('--comment', default=500, help='Quantity of comments, default is 500.')
    def forge(category, post, comment):
        '''Generate fake data.'''
        from app.fakes import fake_admin, fake_categories, fake_posts_and_comments

        db.drop_all()
        db.create_all()

        click.echo('Generating the administrator...')
        fake_admin()

        click.echo('Generating {0} categories...'.format(category))
        fake_categories(category)

        click.echo('Generating {0} posts and {1} comments...'.format(post, comment))
        fake_posts_and_comments(post, comment)

        click.echo('Done.')
