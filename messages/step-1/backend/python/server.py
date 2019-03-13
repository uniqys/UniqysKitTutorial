import json
from bottle import route, run, request, response, static_file, hook
from pymemcache.client import Client

DB_HOST = 'localhost'
DB_PORT = 5652
APP_HOST = 'localhost'
APP_PORT = 5650

db = Client((DB_HOST, DB_PORT))

@route('/api/message')
def get_message():
    message = db.get('message')
    if message is not None:
        decoded = message.decode('utf8')
        return {'message': decoded}
    response.status = 400

@route('/api/message', method='POST')
def post_message():
    sender = request.get_header('uniqys-sender')
    body = request.json
    message = body['message']
    db.set('message', message.encode('utf8'))

run(host=APP_HOST, port=APP_PORT)