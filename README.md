# NuCypher + IPFS


🚀 Welcome to the ncipfs project! 


![logo](ncipfs.png)


## Basic Usage Spec

#### Setup

```
from ncipfs import main

client = main.ncipfs()
```

Connect to Urslas and IPFS Gateway - in this case we connect to two locally running instances
```
client.connect(nucypher_network="localhost:11500",
          ipfs_api_gateway="https://ipfs.infura.io:5001")
```

Now making or loading in an identity is easy
```
client.load_user("alice_ipfs_user/")
```

#### Securing data

we can set the label and contents easily
```
my_label = b'ncipfs_is_awesome.txt'
my_contents = "arbitrary data that is stored on IPFS"
```

now we make a key and add the files to IPFS
```
pubkey = client.make_key_from_label(my_label)
cid = client.add_contents(pubkey, my_contents)
```

#### Permissioning data

Awesome now all we need to do is add the content to that file and we are returned a CID
```
from umbral.keys import UmbralPrivateKey, UmbralPublicKey

enc_privkey = UmbralPrivateKey.gen_key()
sig_privkey = UmbralPrivateKey.gen_key()

enc_pubkey = enc_privkey.get_pubkey()
sig_pubkey = sig_privkey.get_pubkey()

label = b'ncipfs_is_awesome.txt'
m, n = 2, 3

policy = client.create_access_policy(
    enc_pubkey=enc_pubkey, 
    sig_pubkey=sig_pubkey, 
    label=label, 
    m=m, 
    n=n   
)
print(policy)
```

#### Accessing data

We get the recpients identity (with their keys)
```
doctor = client.load_recipent(enc_privkey, sig_privkey)
print(doctor)
```

Lastly we can fetch the files and get them reencrypted for this recpeients access only!
```
message = client.get_file_and_decrypt(doctor, policy, cid)
print(message)
```
