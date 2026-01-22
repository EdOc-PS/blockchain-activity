import sys
import time 
from flask import Flask, jsonify, request
from uuid import uuid4
from blockchain import Blockchain
from flask_cors import CORS

port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000

app = Flask(__name__)
CORS(app)
node_identifier = str(uuid4()).replace('-', '')
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
   
    blockchain.new_transaction(sender="0", recipient=node_identifier, amount=1, content="Recompensa Mineracao")
    block_timestamp = time.time()

    candidate_block = {
        'index': len(blockchain.chain) + 1,
        'timestamp': block_timestamp, 
        'transactions': blockchain.current_transactions,
        'proof': 0,
        'previous_hash': blockchain.hash(last_block),
    }


    proof = blockchain.proof_of_work(candidate_block)

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash, timestamp=block_timestamp)
    block_hash = blockchain.hash(block)

    response = {
        'message': "Novo bloco",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        'hash': block_hash
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required): return 'Faltam valores', 400
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'], values.get('content'))
    return jsonify({'message': f'Transação add ao Bloco {index}'}), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    chain_data = []
    for block in blockchain.chain:
        block_copy = block.copy()
        block_copy['hash'] = blockchain.hash(block)
        chain_data.append(block_copy)
    return jsonify({'chain': chain_data, 'length': len(chain_data)}), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values.get('nodes')
    if nodes is None: return "Erro", 400
    for node in nodes: blockchain.register_node(node)
    return jsonify({'message': 'Nos adicionados', 'total_nodes': list(blockchain.nodes)}), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()
    chain_data = []
    for block in blockchain.chain:
        b = block.copy()
        b['hash'] = blockchain.hash(block)
        chain_data.append(b)
    if replaced: return jsonify({'message': 'Cadeia substituida', 'new_chain': chain_data}), 200
    else: return jsonify({'message': 'Cadeia mantida', 'chain': chain_data}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)