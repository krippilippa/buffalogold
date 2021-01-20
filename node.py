import asyncio

from buffalogold.blockchain import Blockchain
from buffalogold.connections import ConnectionPool
from buffalogold.peers import P2PProtocol
from buffalogold.server import Server

# Instantiate the blockchain and our pool for "peers"
blockchain = Blockchain()
connection_pool = ConnectionPool()

# Instantiate the blockchain and "bolt on" our modules
server = Server(blockchain, connection_pool, P2PProtocol)


async def main():
    # Start the server
    await server.listen()

asyncio.run(main())
