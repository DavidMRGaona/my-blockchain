from typing import List, Any
from flask import Flask, request
from hashlib import sha256
import json
import time
import requests


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash):
        """"
        Constrictor de la clase 'Block'.
        :param index: ID único del bloque.
        :param transactions: Lista de transacciones.
        :param timestamp: momento en que el bloque fue generado.
        """
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        # Agregamos un campo para el hash del bloque anterior
        self.previous_hash = previous_hash

    @staticmethod
    def compute_hash(block):
        """"
        Convierte el bloque en una cadena JSON y luego retorna el hash del mismo.
        La cadena equivalente también considera el campo previous_hash, pues self.__dict__ devuelve todos los campos
        de la clase.
        """
        block_string = json.dumps(block.__dict__, sort_keys=True)

        return sha256(block_string.encode()).hexdigest()


class Blockchain:
    # Dificultad del algoritmo de prueba de trabajo
    difficulty = 2
    unconfirmed_transactions: List[Any]

    def __init(self):
        """"
        Constrictor para la clase 'Blockchain'
        """
        self.unconfirmed_transactions = []
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        """"
        Una función para generar el bloque génesis y añadirlo a la cadena. El bloque tiene index 0, previous_hash 0 y
        un hash válido.
        """
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        """"
        Una forma rápida y pythonica de retornar el bloque más reciente de la cadena.
        Nótese que la cadena siempre contendrá al menos un último bloque (o el bloque génesis)
        """
        return self.chain[-1]

    @staticmethod
    def proof_of_work(block):
        """"
        Función que intenta distintos valores de nonce hasta obtener un hash que satisfag nuestro criterio de dificultad
        """
        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startsWith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return computed_hash

    def add_block(self, block, proof):
        """
        Agrega el bloque a la cadena luego de realizar la verivicación.
        La verificación incluye:
        * Comprobar que la prueba es válida
        * El valor del previous_hash del bloque coincide con el hasth del último bloque de la cadena
        """
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not self.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    @staticmethod
    def is_valid_proof(block, block_hash):
        """
        Comprobar si block_hash es un hash válido y satisfce nuestro criterio de dificultad
        """
        return block_hash.startswith('0' * Blockchain.difficulty) and block_hash == block.compute_hash()

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    def mine(self):
        """
        Esta functión sirve como una interfaz para añadir las transacciones pendientes a la blockchain añadiéndolas al
        bloque y claculando la prueba de trabajo
        """
        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block

        new_block = Block(index=last_block + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []
        announce_new_block(new_block)
        return new_block.index


# Inicializamos la aplicación Flask.
app = Flask(__name__)

# Inicializamos el objeto Blockchain.
blockchain = Blockchain()


# Método de Flask para declarar los puntos de acceso.
@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    required_fields = ['author', 'content']

    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction data", 404

        tx_data['timestamp'] = time.time()

        blockchain.add_new_transaction(tx_data)

    return "Success", 201


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)

    return json.dumps({
        "length": len(chain_data),
        "chain": chain_data
    })


@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "No transaction to mine"

    return "Block #{} is mined".format(result)


@app.route('/pending-tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


# Contiene las direcciones de otros compañeros que participan en la red.
peers = set()


# Punto de acceso para adir nuevos compañeros a la red.
@app.route('/register_node', methods=['POST'])
def register_new_peers():
    # La dirección del nodo compañero.
    node_address = request.get_json()['node_address']
    if not node_address:
        return "Invalid data", 400

    # Añadir el nodo a la lista de compañeros.
    peers.add(node_address)

    # Retornar el blockchain al nuevo nodo registrado para que pueda sincronizar.
    return get_chain()


@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """
    Internamente llama al punto de acceso '/register_node' para registrar el nodo actual con el nodo remoto
    especificado en la petición, y sincronizar el blockchain a si mismo con el nodo remote
    """
    node_address = request.get_json()['node_address']
    if not node_address:
        return "Invalid data", 400

    data = {'node_address': request.host_url}
    headers = {'Content-Type': 'application/json'}

    # Hacer una petición para registrarse en el nodo remoto y obtener información
    response = requests.post(node_address + '/register_node', data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers
        # Actualizar la cadena y los compañeros.
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)
        peers.update(response.json()['peers'])
        return "Registration successful", 200
    else:
        # Si algo sale mal, lo pasamos a la respuesta de la API
        return response.content, response.status_code


def create_chain_from_dump(chain_dump):
    blockchain = Blockchain()
    for idx, block_data in enumerate(chain_dump):
        block = Block(block_data['index'],
                      block_data['transactions'],
                      block_data['timestamp'],
                      block_data['previous_hash'])
        proof = block_data['hash']
        if idx > 0:
            added = blockchain.add_block(block, proof)
            if not added:
                raise Exception("The chain dump is tampered!")
        else:  # El bloque es un bloque génesis, no necesita verificación
            blockchain.chain.append(block)

    return blockchain


def consensus():
    """
    Simple algoritmo de consenso. Si una cadena válida más larga es encontrada, la nuestra es reemplazada por ella.
    """
    global blockchain

    longest_chain = None
    current_len = len(blockchain)

    for node in peers:
        response = requests.get('http://{}/chain'.format(node))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain

        if longest_chain:
            blockchain = longest_chain
            return True

    return False


# Punto de acceso para añadir un bloque minado por alguien más a la cadena del nodo.
@app.route('/add_block', methods=['POST'])
def validate_and_add_block():
    block_data = request.get_json()
    block = Block(block_data['index'],
                  block_data['transactions'],
                  block_data['timestamp'],
                  block_data['previous_hash'])
    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201


def announce_new_block(block):
    for peer in peers:
        url = "http://{}/add_block".format(peer)
        requests.post(url, data=json.dumps(block.__dict__, sort_keys=True))


app.run(debug=True, port=8000)
