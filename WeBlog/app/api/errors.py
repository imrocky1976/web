from flask import jsonify
from app.exceptions import ValidationError
from . import api

# 404 和 500 不在此实现， 由flask自己生成
# e.g. post = Post.query.get_or_404(id)   500 - 处理请求的过程中发生意外错误; 404 - URL 对应的资源不存在

def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response


def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])
