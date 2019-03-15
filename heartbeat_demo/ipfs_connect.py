import ipfsapi
    
try:
    ipfs_gateway_api = ipfsapi.connect('127.0.0.1', 5001)
except Exception as e: # should be more specific ConnectionRefusedError, NewConnectionError, MaxRetryError not sure
    print("Automatic Mode A Public Gateway will be used as a fallback")
    ipfs_gateway_api = ipfsapi.connect('https://ipfs.infura.io', 5001)


