import json
from bottle import route, run, request, response, static_file, hook
from pymemcache.client import Client

DB_HOST = 'localhost'
DB_PORT = 5652
APP_HOST = 'localhost'
APP_PORT = 5650

class Dao:
    def __init__(self, host, port):
        self.db = Client(
            (host, port),
            default_noreply=False,
            serializer=self.__json_serializer,
            deserializer=self.__json_deserializer
        )

    def __json_serializer(self, key, value):
        if type(value) == str:
            return value, 1
        return json.dumps(value), 2

    def __json_deserializer(self, key, value, flags):
        if flags == 1:
            return value.decode('utf-8')
        if flags == 2:
            return json.loads(value.decode('utf-8'))
        raise Exception('Unknown serialization format')

    def get_count(self):
        count = self.db.get('count')
        return int(count) if count else 0

    def get_messages(self, count):
        ids = range(1, count+1)
        result = self.db.get_multi([f'messages:{id}' for id in ids])
        return [{'id': id, **result[f'messages:{id}']} for id in ids]

    def incr_count(self):
        count = self.db.get('count')
        if count:
            return self.db.incr('count', 1)
        else:
            self.db.set('count', 1)
            return 1

    def set_message(self, count, messages):
        self.db.set('messages:'+str(count), messages)

dao = Dao(DB_HOST, DB_PORT)

@route('/api/message')
def get_message():
    count = dao.get_count()
    messages = dao.get_messages(count)
    return {'messages': messages}


@route('/api/message', method='POST')
def post_message():
    count = dao.incr_count()
    body = request.json

    messages = {
            'sender': request.get_header('uniqys-sender'),
            'timestamp': request.get_header('uniqys-timestamp'),
            'blockhash': request.get_header('uniqys-blockhash'),
            'contents': body['message']
    }

    dao.set_message(count, messages)

run(host=APP_HOST, port=APP_PORT, debug=True, reloader=True)