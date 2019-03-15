# NuCypher + IPFS


We aim to provider a simple interface between IPFS and NuCypher. In this project we have a dev copy of nucypher which we run in federated mode. 

This demo just replaces the filestore in the heartbeat demo with IPFS as the filestore.

## Deploying Local Fleet

```
git clone https://github.com/nucypher/nucypher.git
cd nucypher
pipenv install
pipenv shell
```

now we start the fleet
```
sh scripts/local_fleet/run_local_fleet.sh 
```

you should see 

```
(nucypher) bash-3.2$ sh scripts/local_fleet/run_local_fleet.sh 
Starting Local Development Fleet...
Starting Lonely Ursula...
Starting Ursula #2...
Starting Ursula #3...
(nucypher) bash-3.2$ historu
```

## Setup Edited Example

awesome, now in the same console we'll open the `ipfs` enabled app...


```
git clone https://github.com/drbh/nucypher-ipfs.git

cd nucypher-ipfs
pipenv install --skip-lock
pipenv shell
```

## Running Edited Example


### Alice creates policy and device write heartbeat data to IPFS

```
python heartbeat_demo/alicia.py 
```

*ps: you'll also see 3 json files get created that are the keys and policy pretaining this data*

new output will show the `CID` of the bytes that were written to IPFS
```
🚀 ADDING TO IPFS D-STORAGE NETWORK 🚀
File Address:	QmYYri78XX8uyDDEPHsbeuaujtENwhgzGPRtRhPiA1NBVy
```

*you can check that its really in IPFS by fetching it from a gateway*
```
http://cloudflare-ipfs.com/ipfs/QmYYri78XX8uyDDEPHsbeuaujtENwhgzGPRtRhPiA1NBVy
```

A 13kb file should download (assuming it still cached - or use your own hash) and it is the encrypted heartbeat data. 


## The Doctor now reads the file from IPFS and can decrypt

```
python heartbeat_demo/doctor.py QmYYri78XX8uyDDEPHsbeuaujtENwhgzGPRtRhPiA1NBVy
```


```
🚀 FETCHING FROM IPFS D-STORAGE NETWORK 🚀
Accessing File:	QmYYri78XX8uyDDEPHsbeuaujtENwhgzGPRtRhPiA1NBVy
```


yay you'll get an output like
```

----------------------------------❤︎ (77 BPM)                                                Retrieval time:    92.84 ms
--------------------------------❤︎ (76 BPM)                                                  Retrieval time:    94.02 ms
------------------------------------------❤︎ (81 BPM)                                        Retrieval time:    92.02 ms
----------------------------------------❤︎ (80 BPM)                                          Retrieval time:    92.81 ms
------------------------------------❤︎ (78 BPM)                                              Retrieval time:    97.02 ms
------------------------------------❤︎ (78 BPM)                                              Retrieval time:    98.01 ms
--------------------------------❤︎ (76 BPM)                                                  Retrieval time:    95.03 ms
--------------------------------------❤︎ (79 BPM)                                            Retrieval time:    91.29 ms
----------------------------------------❤︎ (80 BPM)                                          Retrieval time:   105.53 ms
--------------------------------------❤︎ (79 BPM)                                            Retrieval time:    91.50 ms
```

# Next Steps

This is just a POC to test the `ipfsapi` Python package with NuCypher. There should be some work done to standardize this datasource. Also more complex ACL like a folder with many files.

In this POC we also implemented a tiny failover feature, where if no IPFS node is running locally it fallsback to infuras IPFS gateway.


