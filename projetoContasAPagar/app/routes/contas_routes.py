from flask import Blueprint, render_template

bp = Blueprint('contas', __name__, url_prefix='/contas')

@bp.route('/')
def index():
    return render_template('contas/list.html')
