import hashlib
import json
from time import time
from urllib.parse import urlparse
import requests

class Blockchain:
    def __init__(self):
 
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

        genesis_prev = '0' * 64
        genesis_candidate = {
            'index': 1,
            'timestamp': 0,
            'transactions': [],
            'proof': 0,
            'previous_hash': genesis_prev
        }
        

        proof = self.proof_of_work(genesis_candidate)
        
        self.new_block(previous_hash=genesis_prev, proof=proof, timestamp=0)

    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            if block['previous_hash'] != self.hash(last_block):
                return False
     
            if not self.valid_proof(block):
                return False
            last_block = block
            current_index += 1
        return True

    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)

        for node in neighbours:
            try:
                response = requests.get(f'http://{node}/chain')
                if response.status_code == 200:
                    length = response.json()['length']
                    chain = response.json()['chain']

                    for block in chain:
                        if 'hash' in block: del block['hash']

                    if length > max_length and self.valid_chain(chain):
                        max_length = length
                        new_chain = chain
            except:
                continue

        if new_chain:
            self.chain = new_chain
            return True
        return False

    def new_block(self, proof, previous_hash=None, timestamp=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': timestamp if timestamp is not None else time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount, content=None):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'content': content
        })
        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
   
    def proof_of_work(self, block):
        block['proof'] = 0
        while self.valid_proof(block) is False:
            block['proof'] += 1
        return block['proof']

    @staticmethod
    def valid_proof(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        guess_hash = hashlib.sha256(block_string).hexdigest()
        return guess_hash[:4] == "0000"