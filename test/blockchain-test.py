# -*- coding: utf-8 -*-

"""
    tests for Blockchain

"""

import json
import sys
sys.path.extend([".", ".."])
import unittest
import inspect
# from ensure import ensure
from src.blockchain.blockchain import Blockchain




class BlockchainTestCase(unittest.TestCase):

    def setUp(self):
        self.bc1 = Blockchain()
        self.bc2 = Blockchain()
        self.bc3 = Blockchain()

    def test_new_node(self):
        print("\n Running Test Method : " + inspect.stack()[0][3])
        self.bc1.register_node('192.168.0.5:5000')
        self.bc1.register_node('localhost:5001')
        self.assertIsInstance(self.bc1.nodes, set)
        self.bc1.register_node('localhost:5001')
        self.assertTrue(len(self.bc1.nodes) == 2)
        self.assertTrue('localhost:5001' in self.bc1.nodes)
        self.assertTrue('localhost:5000' not in self.bc1.nodes)

    def test_valid_chain(self):
        print("\n Running Test Method : " + inspect.stack()[0][3])
        c = 0
        while c < 5:
            self.bc1.new_block(self.bc1.proof_of_work(self.bc1.last_block))
            self.bc1.new_transaction("Beatrice", "Amanda", 3)
            self.bc2.new_block(self.bc2.proof_of_work(self.bc2.last_block))
            self.bc2.new_transaction("Amanda", "Me", 2)
            self.bc3.new_block(self.bc2.proof_of_work(self.bc2.last_block))
            self.bc3.new_transaction("Amanda", "Me", 5)
            c += 1
        self.assertEqual(self.bc1.valid_chain(self.bc1.chain), True)
        self.assertTrue(self.bc1.valid_chain(self.bc2.chain))
        self.assertFalse(self.bc3.valid_chain(self.bc3.chain))

    def test_resolve(self):
        pass

    def test_new_block(self):
        print("\n Running Test Method : " + inspect.stack()[0][3])
        self.bc1.new_block(0)
        self.bc1.new_block('1')
        self.bc1.new_block('abc')
        self.bc1.new_block(json.dumps(self.bc1.chain[1], sort_keys=True))
        self.assertEqual(len(self.bc1.chain), 5)
        self.assertEqual(self.bc1.chain[0]['previous_hash'], '1')
        self.assertEqual(self.bc1.hash(self.bc1.chain[0]), self.bc1.chain[1]['previous_hash'])
        self.assertEqual(self.bc1.hash(self.bc1.chain[1]), self.bc1.chain[2]['previous_hash'])
        self.assertEqual(self.bc1.hash(self.bc1.chain[2]), self.bc1.chain[3]['previous_hash'])
        self.assertEqual(self.bc1.hash(self.bc1.chain[3]), self.bc1.chain[4]['previous_hash'])

    def test_new_transaction(self):
        print("\n Running Test Method : " + inspect.stack()[0][3])
        self.bc1.new_transaction('sender1', 'receiver1', 2)
        self.assertEqual(json.dumps(self.bc1.current_transactions),
                         '[{"sender": "sender1", "recipient": "receiver1", "amount": 2}]')
        self.bc1.new_transaction('sender2', 'receiver2', 3)
        self.assertEqual(json.dumps(self.bc1.current_transactions[1]),
                         '{"sender": "sender2", "recipient": "receiver2", "amount": 3}')
        self.bc2.new_transaction('Bobby', 'receiver3', 4)
        self.assertEqual(json.dumps(self.bc2.current_transactions, sort_keys=True),
                         '[{"amount": 4, "recipient": "receiver3", "sender": "Bobby"}]')
        self.bc2.new_transaction('Jill', 'Me', 7)
        self.assertEqual(json.dumps(self.bc2.current_transactions, sort_keys=True),
                         '[{"amount": 4, "recipient": "receiver3", "sender": "Bobby"}, {"amount": 7, "recipient": "Me", "sender": "Jill"}]')
        self.assertEqual(self.bc2.current_transactions[0]["sender"], "Bobby")
        self.assertEqual(self.bc2.current_transactions[1]["sender"], "Jill")
        self.assertEqual(self.bc2.current_transactions[1]["recipient"], "Me")
        self.assertEqual(self.bc2.current_transactions[0]["amount"], 4)
        self.assertEqual(self.bc1.last_block['index'], 1)
        self.assertEqual(self.bc2.new_transaction("Alpha", "Bravo", 12), 2)
        self.assertEqual(len(self.bc1.current_transactions), 2)
        self.assertEqual(len(self.bc2.current_transactions), 3)

    def test_last_block(self):
        print("\n Running Test Method : " + inspect.stack()[0][3])
        self.assertTrue(self.bc1.last_block["index"] == 1)
        self.bc2.new_block("abc")
        self.assertTrue(self.bc2.last_block["index"] == 2)
        self.bc2.new_transaction("Jill", "Me", 15)
        self.bc2.new_block(35)
        self.assertTrue(self.bc2.last_block["index"] == 3)
        self.assertEqual(self.bc2.last_block["transactions"], [{'sender': 'Jill', 'recipient': 'Me', 'amount': 15}])
        self.bc1.new_transaction("Jill", "Me", 15)
        self.bc1.new_transaction("Amanda", "Me", 20)
        self.bc1.new_block('1234')
        self.assertTrue(len(self.bc1.last_block["transactions"]) == 2)
        self.assertTrue(self.bc1.last_block["transactions"][1]["sender"] == "Amanda")
        self.assertEqual(self.bc1.last_block["transactions"][0]["recipient"],
                         self.bc1.last_block["transactions"][1]["recipient"])

    def test_hash(self):
        # print(f'\nb: {json.dumps(self.bc1.chain, sort_keys=True)}')
        print("\n Running Test Method : " + inspect.stack()[0][3])
        self.assertEqual(self.bc1.hash(0), '5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9')
        self.assertEqual(self.bc2.hash('0'), '98089e6d36f78e9766c9ea34d5acb3611f3a92cd81c5eb102095d924ffc7d08b')
        self.assertEqual(self.bc1.hash(1), '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b')
        self.assertEqual(self.bc2.hash('1'), self.bc2.hash('1'))
        self.assertEqual(self.bc2.hash(100), 'ad57366865126e55649ecb23ae1d48887544976efea46a48eb5d85a6eeb4d306')
        self.assertEqual(self.bc2.hash('100'), self.bc1.hash('100'))
        self.assertEqual(len(self.bc1.hash('abcdefg')), 64)
        self.assertEqual(len(self.bc2.hash(12)), 64)

    def test_proof_of_work(self):
        print("\n Running Test Method : " + inspect.stack()[0][3])
        self.bc1.last_block['timestamp'] = 0
        c = 0
        while c < 5:
            self.bc1.new_block(self.bc1.proof_of_work(self.bc1.last_block))
            self.bc1.last_block['timestamp'] = 0
            c += 1
        self.assertEqual(self.bc1.chain[1]['proof'], 504932)
        self.assertEqual(self.bc1.chain[2]['proof'], 15930)
        self.assertEqual(self.bc1.chain[3]['proof'], 62459)

    def test_valid_proof(self):
        print("\n Running Test Method : " + inspect.stack()[0][3])
        c = 0
        while c < 5:
            self.bc1.new_block(self.bc1.proof_of_work(self.bc1.last_block))
            c += 1
        self.assertEqual(len(self.bc1.chain), 6)
        self.assertEqual(self.bc1.valid_proof(self.bc1.chain[-2]['proof'], self.bc1.last_block['proof'],
                                              self.bc1.last_block['previous_hash']), True)

    def test_chain(self):
        print("\n Running Test Method : " + inspect.stack()[0][3])
        self.setUp()
        self.assertEqual(len(self.bc1.chain), 1, msg="1st blockchain initial length should be 1")
        self.assertIsInstance(self.bc1, Blockchain, msg="bc1 is a Blockchain")
        self.assertEqual(len(self.bc2.chain), 1, msg="2nd blockchain initial length should be 1")
        self.assertIsInstance(self.bc2, Blockchain, msg="bc2 is a Blockchain")

    def tearDown(self):
        del self.bc1
        del self.bc2
        # gc.collect()


if __name__ == '__main__':
    unittest.main(verbosity=2)
