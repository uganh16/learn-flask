import random

from faker import Faker
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Admin, Category, Comment, Post
from app.utils import random_split


fake = Faker()


def fake_admin():
    admin = Admin(
        username='admin',
        blog_title='Bluelog',
        blog_sub_title="No, I'm the real thing.",
        name='Mima Kirigoe',
        about='Um, l, Mima Kirigoe, had a fun time as a member of CHAM...'
    )
    admin.set_password('admin')
    db.session.add(admin)
    db.session.commit()


def fake_categories(count=10):
    category = Category(name='Default')
    db.session.add(category)

    for _ in range(count):
        category = Category(name=fake.word())
        db.session.add(category)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_posts(count=50):
    for _ in range(count):
        post = Post(
            title=fake.sentence(),
            body=fake.text(2000),
            timestamp=fake.date_time_this_year(),
            category=Category.query.get(random.randint(1, Category.query.count())),
        )
        db.session.add(post)
    db.session.commit()


def fake_posts_and_comments(post_count, comment_count):
    admin = Admin.query.first()

    for n in random_split(comment_count, post_count):
        post_timestamp = fake.date_time_this_year()
        post = Post(
            title=fake.sentence(),
            body=fake.text(2000),
            timestamp=post_timestamp,
            category=Category.query.get(random.randint(1, Category.query.count())),
        )

        comments = []
        for _ in range(n):
            from_admin = random.random() < 0.2
            replied = None
            if comments and random.random() < 0.35:
                replied = random.choice(comments)
                if not replied.reviewed:
                    replied = None
            reviewed = from_admin or random.random() < 0.75
            comment = Comment(
                author=admin.name if from_admin else fake.name(),
                email=fake.email(), # @todo
                site=fake.url(), # @todo
                body=fake.sentence(),
                from_admin=from_admin,
                reviewed=reviewed,
                timestamp=fake.date_time_between_dates(replied.timestamp if replied else post_timestamp),
                post=post,
                replied=replied
            )
            comments.append(comment)

        db.session.add(post)
        db.session.add_all(comments)

    db.session.commit()
