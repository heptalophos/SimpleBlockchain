# -*- coding: utf-8 -*-

import hashlib
import json

from time import time
from urllib.parse import urlparse


class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        # Create the genesis block
        self.new_block(previous_hash='1', proof=100)
        # A set of nodes (because we want the addition of new nodes to be idempotent)
        self.nodes = set()

    def register_node(self, address):
        """
        Add a new node to a set of nodes

        :param address: <str> Address of node. E.g. 'http://192.168.0.5:5000'
        :return: None 
        """
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid 

        :param chain: <list> A blockchain
        :return: <bool> True if valid, false if not
        """

        last_block = chain[0]
        current_index = 1
        
        while current_index < len(chain):
            block = chain[current_index]
            # print("\n--------------------\n")
            # Check correctness of last block's hash
            if block['previous_hash'] != self.hash(last_block): 
                return False
            # Check correctness of proof-of-work
            # if not self.valid_proof(last_block['proof'], block['proof'], last_block['previous_hash']):
            if not self.valid_proof(last_block['proof'], block['proof'], block['previous_hash']):
                return False
            last_block = block 
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        The Consensus Algorithm, it resolves conflicts by replacing 
        our chain by the longest one in the network

        :return: <bool> True if our chain was replaced, false if not 
        """
        neighbours = self.nodes
        new_chain = None
        # Look only for chains longer than this
        max_length = len(self.chain)
        # Get and verify the chains from all the nodes in the network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                # Check if chain is longer and valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        # Replace this chain if a longer valid chain is discovered
        if new_chain:
            self.chain = new_chain
            return True
        return False

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain

        :param proof: <int> The proof given by the Proof of Work Algorithm
        :param previous_hash: (Optional) <str> The hash of the previous Block
        :return: <dict> New Block
        """
    
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
            }

        # Reset the current list of transactions
        self.current_transactions = []
        # Add block to existing chain
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go to the next mined block

        :param sender: <str> Address of the sender
        :param recipient: <str> Address of the recipient
        :param amount: <int> amount

        :return: <int> The index of the block that will hold this transaction
        """

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @property
    def last_block(self):
        # Returns last block in chain
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block

        :param block: <dict> Block
        :return: <str> The Block's hash
        """
        # The dictionary MUST be ordered, or we can have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_block):
        """
        Simple proof-of-work Algorithm:
        - Find a number p' such that, hash(pp') contains 4 leading 0s, 
        - where p is the previous proof and p' is the new proof

        :param last_block: <dict> last Block 
        :return: <int>
        """

        last_proof = last_block['proof']
        last_hash = self.hash(last_block)

        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        """
        Validates the Proof: Does hash(last_proof, proof) contain 4 leading zeros?

        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :param last_hash: <str> The hash of the Previous Block
        :return: <bool> True if correct, False if not.

        """

        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"



