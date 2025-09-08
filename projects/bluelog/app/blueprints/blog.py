from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from app.extensions import db
from app.forms import AdminCommentForm, CommentForm
from app.models import Category, Comment, Post


bp = Blueprint('blog', __name__)


# @todo skip it
class current_user:
    is_authenticated = False


@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=per_page)
    return render_template('blog/index.html', pagination=pagination, posts=pagination.items)


@bp.route('/about')
def about():
    return render_template('blog/about.html')


@bp.route('/category/<int:category_id>')
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']
    pagination = Post.query.with_parent(category).order_by(Post.timestamp.desc()).paginate(page=page, per_page=per_page)
    return render_template('blog/category.html', category=category, pagination=pagination, posts=pagination.items)


@bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
    post = Post.query.get_or_404(post_id)

    if current_user.is_authenticated:
        form = AdminCommentForm()
        form.author.data = current_user.name
        form.email.data = current_app.config['BLUELOG_EMAIL']
        from_admin = True
        reviewed = True
    else:
        form = CommentForm()
        from_admin = False
        reviewed = False

    if form.validate_on_submit():
        replied = None
        replied_id = request.args.get('reply')
        if replied_id:
            replied = Comment.query.get_or_404(replied_id)
            # @todo send email
        comment = Comment(
            author=form.author.data,
            email=form.email.data,
            body=form.body.data,
            from_admin=from_admin,
            reviewed=reviewed,
            post=post,
            replied=replied,
        )
        db.session.add(comment)
        db.session.commit()
        if current_user.is_authenticated:
            flash('Comment published.', 'success')
        else:
            flash('Thanks, your comment will be published after reviewed.', 'info')
            # @todo send notification email to admin
        return redirect(url_for('.show_post', post_id=post_id))

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_COMMENT_PER_PAGE']
    pagination = Comment.query.with_parent(post).filter_by(reviewed=True).order_by(Comment.timestamp.asc()).paginate(page=page, per_page=per_page)

    return render_template('blog/post.html', post=post, pagination=pagination, form=form, comments=pagination.items)


@bp.route('/reply/comment/<int:comment_id>')
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    return redirect(url_for('.show_post', post_id=comment.post.id, reply=comment_id, author=comment.author) + '#comment-form')
