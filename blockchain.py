import hashlib
import json
import time
import os

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_votes = []
        self.load_chain()

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'votes': self.current_votes,
            'proof': proof,
            'previous_hash': previous_hash
        }
        self.current_votes = []
        self.chain.append(block)
        self.save_chain()
        return block

    def add_new_vote(self, voter, candidate):
        self.current_votes.append({
            'voter': voter,
            'candidate': candidate
        })

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def proof_of_work(self, previous_proof):
        new_proof = 1
        while True:
            hash_op = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_op[:4] == '0000':
                return new_proof
            new_proof += 1

    def get_previous_block(self):
        return self.chain[-1] if self.chain else None

    def mine(self):
        previous_block = self.get_previous_block()
        previous_proof = previous_block['proof'] if previous_block else 1
        proof = self.proof_of_work(previous_proof)
        previous_hash = self.hash(previous_block) if previous_block else '0'
        self.create_block(proof, previous_hash)

    def load_chain(self):
        if os.path.exists('blockchain_data.json'):
            with open('blockchain_data.json', 'r') as f:
                self.chain = json.load(f)
        if not self.chain:
            # ✅ Ensure genesis block has 'proof'
            self.create_block(proof=1, previous_hash='0')

    def save_chain(self):
        with open('blockchain_data.json', 'w') as f:
            json.dump(self.chain, f, indent=4)
