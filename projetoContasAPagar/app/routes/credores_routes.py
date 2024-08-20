from flask import Blueprint, render_template

bp = Blueprint('credores', __name__, url_prefix='/credores')

@bp.route('/')
def index():
    return render_template('credores/list.html')
