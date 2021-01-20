import asyncio
import json
import math
import random

from hashlib import sha256
from time import time

import structlog

logger = structlog.getLogger("blockchain")


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.target = "0000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"

        # Create genesis block
        logger.info("Creating genesis block")
        self.chain.append(self.new_block())

    def new_block(self):
        block = self.create_block(
            height=len(self.chain),
            transactions=self.pending_transactions,
            previous_hash=self.last_block["hash"] if self.last_block else None,
            nonce=format(random.getrandbits(64), "x"),
            target=self.target,
            timestamp=time(),
        )

        # Reset list of pending transactions
        self.pending_transactions = []

        return block

    @ staticmethod
    def create_block(height, transactions, previous_hash, nonce, target, timestamp=None):
        block = {
            'height': height,
            'transactions': transactions,
            'previous_hash': previous_hash,
            'nonce': nonce,
            'target': target,
            'timestamp': timestamp or time(),
        }

        # Get the hash of this new block and add it to the block
        block_string = json.dumps(block, sort_keys=True).encode()
        block["hash"] = sha256(block_string).hexdigest()
        return block

    @ staticmethod
    def hash(block):
        # We ensure the dictionary is sorted or we'll have incosistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return sha256(block_string).hexdigest()

    @ property
    def last_block(self):
        # Returns the last block on the chain, if there are any
        return self.chain[-1] if self.chain else None

    def valid_block(self, block):
        # Checks if block's hash is less than the target
        return block["hash"] < self.target

    def add_block(self, block):
        # TODO: add proper validation logic here!
        self.chain.append(block)

    def recalculate_target(self, block_index):
        """
        Returns the nuber we need to get below to mine a block
        """

        # Chek if we need to recalculate toe target
        if block_index % 10 == 0:
            # Expected time span of 10 blocks
            expected_timespan = 10 * 10

            # Calculate the actual time span
            actual_timespan = self.chain[-1]["timestamp"] - \
                self.chain[-10]["timestamp"]

            # Figure out what the offset is
            ratio = actual_timespan / expected_timespan

            # Now let's adjust the ratio to not be too extreme
            ratio = max(0.25, ratio)
            ratio = min(4.00, ratio)

            # Calculate the new target by multiplying the current one by the ratio
            new_target = int(self.target, 16) * ratio

            self.target = format(math.floor(new_target), "x").zfill(64)
            logger.info(f"Calculated new minig target: {self.target}")

    def proof_of_work(self):
        while True:
            new_block = self.new_block()
            if self.valid_block(new_block):
                break

        self.chain.append(new_block)
        print("Found a new block: ", new_block)

    def new_transaction(self, sender, recipient, amount):
        # Adds a new transaction to the list of pending transactions
        self.pending_transactions.append({
            "recipient": recipient,
            "sender": sender,
            "amount": amount,
        })
