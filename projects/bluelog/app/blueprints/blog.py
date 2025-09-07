from flask import Blueprint, abort, flash, render_template


bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    return render_template('blog/index.html')


@bp.route('/about')
def about():
    return render_template('blog/about.html')


@bp.route('/category/<int:category_id>')
def show_category(category_id):
    abort(404)
