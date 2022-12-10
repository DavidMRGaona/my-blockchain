from hashlib import sha256
import json
import time


class Block:
    def __int__(self, index, transactions, timestamp, previous_hash):
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

    def __init(self):
        """"
        Constrictor para la clase 'Blockchain'
        """
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
