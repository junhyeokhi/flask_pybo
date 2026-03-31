from flask import Blueprint

bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/')
def index():
    return 'Hello index!'

@bp.route('/hello')
def hello_world():
    return 'Hello Pybo!'

@bp.route('/pay')
def pay():
    return '결제 페이지 입니다!'

@bp.route('/test')
def test():
    return '테스트해보겠습니다.'