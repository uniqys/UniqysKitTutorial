import json
import hashlib
import requests
from bottle import route, run, request, response, static_file, hook
from pymemcache.client import Client

DB_HOST = 'localhost'
DB_PORT = 5652
APP_HOST = 'localhost'
APP_PORT = 5650
INNER_API_HOST = 'localhost'
INNER_API_PORT = 5651
OPERATOR_ADDRESS = 'b8e6493bf64cae685095b162c4a4ee0645cde586'

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

    def get_sushi_list(self, count):
        ids = range(1, count+1)
        result = self.db.get_multi([f'sushi:{id}' for id in ids])
        return [{'id': id, **result[f'sushi:{id}']} for id in ids]

    def incr_count(self):
        count = self.db.get('count')
        if count:
            return self.db.incr('count', 1)
        else:
            self.db.set('count', 1)
            return 1

    def set_sushi(self, sushi):
        self.db.set('sushi:'+str(sushi['id']), sushi)

dao = Dao(DB_HOST, DB_PORT)

def transfer_gari(sender, to, value):
    uri = 'http://'+INNER_API_HOST+':'+str(INNER_API_PORT)+'/accounts/'+str(sender)+'/transfer'
    response = requests.post(
        uri,
        data=json.dumps(dict({'to': str(to), 'value': int(value)})),
        headers={'Content-Type': 'application/json'})

@route('/api/gari')
def get_gari():
    address = request.query.address
    uri = 'http://'+INNER_API_HOST+':'+str(INNER_API_PORT)+'/accounts/'+str(address)+'/balance'
    response = requests.get(uri)
    balance = response.json()[0]
    return {'balance': balance}

@route('/api/tap', method='POST')
def tap_gari():
    sender = request.get_header('uniqys-sender')
    uri = 'http://'+INNER_API_HOST+':'+str(INNER_API_PORT)+'/accounts/'+str(sender)+'/balance'
    response = requests.put(uri, data=json.dumps([10000]), headers={'Content-Type': 'application/json'})
    return 0

@route('/api/sushiList')
def get_sushi_list():
    count = dao.get_count()
    sushi_list = dao.get_sushi_list(count)
    return {'sushiList': sushi_list}

@route('/api/generate', method='POST')
def post_sushi():
    count = dao.incr_count()
    keccak_hash = hashlib.sha3_256()
    keccak_hash.update(str(count).encode('utf-8'))
    owner = request.get_header('uniqys-sender')
    dna = keccak_hash.hexdigest()

    sushi = {
            'id': count,
            'status': 'normal',
            'price': 0,
            'owner': owner,
            'dna': dna,
            'timestamp': request.get_header('uniqys-timestamp'),
            'blockhash': request.get_header('uniqys-blockhash')
    }
    dao.set_sushi(sushi)

    transfer_gari(owner, OPERATOR_ADDRESS, 100)

    return 0

@route('/api/sell', method='POST')
def sell_sushi():
    data = request.json
    sushi = data['sushi']
    price = data['price']

    new_sushi = sushi
    new_sushi['status'] = 'sell'
    new_sushi['price'] = price

    dao.set_sushi(new_sushi)

@route('/api/buy', method='POST')
def buy_sushi():
    sender = request.get_header('uniqys-sender')

    data = request.json
    sushi = data['sushi']
    seller = sushi['owner']
    price = int(sushi['price'])

    new_sushi = sushi
    new_sushi['status'] = 'normal'
    new_sushi['price'] = 0
    new_sushi['owner'] = sender

    dao.set_sushi(new_sushi)

    transfer_gari(sender, seller, price)

    return 0

run(host=APP_HOST, port=APP_PORT, debug=True, reloader=True)