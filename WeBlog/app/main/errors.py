from flask import render_template, request, jsonify
from . import main

def request_wants_json():
    header = request.accept_mimetypes.to_header()
    if header == 'application/json,*/*':
        return True

    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']

@main.app_errorhandler(403)
def forbidden(e):
    #if request.accept_mimetypes.accept_json and \
    #        not request.accept_mimetypes.accept_html:
    if request_wants_json():
        response = jsonify({'error': 'forbidden'})
        response.status_code = 403
        return response
    return render_template('403.html'), 403

@main.app_errorhandler(404)
def page_not_found(e):
    if request_wants_json():
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    if request_wants_json():
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    return render_template('500.html'), 500
