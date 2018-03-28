import sys
import requests

from uuid import uuid4
from flask import Flask, jsonify, request
from blockchain.blockchain import Blockchain

# Instantiate node
app = Flask(__name__)

# Generate globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the blockchain
blockchain = Blockchain()

# Define the endpoints ##

@app.route('/')
def home():
    return "Hello, Blockchain", 200


@app.route('/mine', methods=['GET'])
def mine():
    # Run the proof-of-work algorithm to get the next proof
    last_block = Blockchain.last_block
    proof = Blockchain.proof_of_work(last_block)

    # Receive a reward for finding the proof
    # A sender "0" signifies that the node has mined a new coin
    Blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )
    
    # Forge a new block by adding transaction to the chain
    previous_hash = Blockchain.hash(last_block)
    block = Blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }

    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Are the required fields in the POSTed data?
    required = ['sender', 'receiver', 'amount']
    if not all(k in values for k in required):
        return 'Missing Values', 400

    # Create a new transaction
    index = Blockchain.new_transaction(values['sender'], values['receiver'], values['amount'])
    response = {'message': f'Transaction will be added to Block {index}'}
    
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': Blockchain.chain,
        'length': len(Blockchain.chain),
    }
    return jsonify(response), 201


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    print(f'Values is: {values}')
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400
    for node in nodes:
        Blockchain.register_node(node)
    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(Blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = Blockchain.resolve_conflicts()
    if replaced:
        response = {
            'message': 'Chain was replaced',
            'new_chain': Blockchain.chain
        }
    else:
        response = {
            'message': 'Chain is authoritative',
            'chain': Blockchain.chain
        }
    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='localhost', port=port)


