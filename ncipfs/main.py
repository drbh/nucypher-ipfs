import maya
import msgpack
import ipfsapi
import shutil
import os
import time
import datetime

from timeit import default_timer as timer

from nucypher.characters.lawful import Enrico
from nucypher.characters.lawful import Bob, Ursula
from nucypher.config.characters import AliceConfiguration
from nucypher.crypto.powers import DecryptingPower, SigningPower
from nucypher.network.middleware import RestMiddleware
from nucypher.utilities.logging import SimpleObserver
from nucypher.crypto.kits import UmbralMessageKit
from nucypher.keystore.keypairs import DecryptingKeypair, SigningKeypair
from umbral.keys import UmbralPublicKey



class ncipfs(object):
	"""docstring for ncipfs"""
	def __init__(self):
		self.name = "David"
		pass

	def connect(self, nucypher_network, ipfs_api_gateway): 
		"""
		client = ncipfs.Connect(
			nucypher_network="localhost:11500",
			ipfs_api_gateway="localhost:5001"
		)
		"""
		self.nucypher_network = nucypher_network
		self.ipfs_api_gateway = ipfs_api_gateway

		try:
			self.ipfs_gateway_api = ipfsapi.connect('127.0.0.1', 5001)
		except Exception as e: # should be more specific ConnectionRefusedError, NewConnectionError, MaxRetryError not sure
			print("Automatic Mode A Public Gateway will be used as a fallback")
			self.ipfs_gateway_api = ipfsapi.connect('https://ipfs.infura.io', 5001)


		SEEDNODE_URL = self.nucypher_network
		POLICY_FILENAME = "policy-metadata.json"

		self.ursula = Ursula.from_seed_and_stake_info(seed_uri=SEEDNODE_URL,
												 federated_only=True,
												 minimum_stake=0)

		return True

	def load_user(self, dirname): 
		"""
		me = client.load_user(
			dirname="/tmp/heartbeat-demo-alice/"
		)
		"""
		passphrase = "TEST_ALICIA_INSECURE_DEVELOPMENT_PASSWORD"
		shutil.rmtree(dirname, ignore_errors=True)

		alice_config = AliceConfiguration(
			config_root=os.path.join(dirname),
			is_me=True,
			known_nodes={self.ursula},
			start_learning_now=False,
			federated_only=True,
			learn_on_same_thread=True,
		)
		alice_config.initialize(password=passphrase)
		alice_config.keyring.unlock(password=passphrase)
		alicia = alice_config.produce()
		alice_config_file = alice_config.to_configuration_file()
		alicia.start_learning_loop(now=True)
		self.alicia = alicia
		return self.alicia 


	def make_key_from_label(self, label): 
		"""
		policy_pub_key = client.make_key_from_label(
			label="mydata"
		)
		"""
		policy_pubkey = self.alicia.get_policy_pubkey_from_label(label)
		print("The policy public key for "
			  "label '{}' is {}".format(label.decode("utf-8"), policy_pubkey.to_bytes().hex()))
		return policy_pubkey


	def add_contents(self, policy_pubkey, contents): 
		"""
		cid = client.add_contents(
			policy_pubkey=policy_pub_key
		)
		"""
		data_source = Enrico(policy_encrypting_key=policy_pubkey)
		data_source_public_key = bytes(data_source.stamp)
		heart_rate = 80
		now = time.time()
		kits = list()
		heart_rate = contents
		now += 3
		heart_rate_data = { 'heart_rate': heart_rate, 'timestamp': now, }
		plaintext = msgpack.dumps(heart_rate_data, use_bin_type=True)
		message_kit, _signature = data_source.encrypt_message(plaintext)
		kit_bytes = message_kit.to_bytes()
		kits.append(kit_bytes)
		data = { 'data_source': data_source_public_key, 'kits': kits, }
		print("🚀 ADDING TO IPFS D-STORAGE NETWORK 🚀")
		d = msgpack.dumps(data, use_bin_type=True)
		cid = self.ipfs_gateway_api.add_bytes(d)
		print("File Address:\t%s" % cid)
		return cid

	def create_access_policy(self, enc_pubkey, sig_pubkey, label, m, n):
		"""
		policy = client.create_access_policy(
			enc_pubkey=enc_pubkey,
			sig_pubkey=sig_pubkey,
			label=label,
			m=m,
			n=n,
		)
		"""
		powers_and_material = { DecryptingPower: enc_pubkey, SigningPower: sig_pubkey }
		doctor_strange = Bob.from_public_keys(powers_and_material=powers_and_material, federated_only=True)
		policy_end_datetime = maya.now() + datetime.timedelta(days=5)
		m, n = 2, 3
		print("Creating access policy for the Doctor...")
		policy = self.alicia.grant(bob=doctor_strange, label=label, m=m, n=n, expiration=policy_end_datetime)
		policy_info = {
			"policy_pubkey": policy.public_key.to_bytes().hex(),
			"alice_sig_pubkey": bytes(self.alicia.stamp).hex(),
			"label": label.decode("utf-8"),
		}
		return policy_info

	def load_recipent(self, enc_privkey, sig_privkey):
		"""
		doctor = client.load_recipent(
			enc_pubkey=enc_pubkey,
			sig_pubkey=sig_pubkey
		)
		"""
		bob_enc_keypair = DecryptingKeypair(private_key=enc_privkey)
		bob_sig_keypair = SigningKeypair(private_key=sig_privkey)
		enc_power = DecryptingPower(keypair=bob_enc_keypair)
		sig_power = SigningPower(keypair=bob_sig_keypair)
		power_ups = [enc_power, sig_power]
		# print("Creating the Doctor ...")
		doctor = Bob(
			is_me=True,
			federated_only=True,
			crypto_power_ups=power_ups,
			start_learning_now=True,
			abort_on_learning_error=True,
			known_nodes=[self.ursula],
			save_metadata=False,
			network_middleware=RestMiddleware(),
		)
		# print("Doctor = ", doctor)
		return doctor

	def get_file_and_decrypt(self, doctor, policy, ipfs_hash):
		"""
		message = client.get_file_and_decrypt(
			doctor=doctor, 
			policy=policy, 
			ipfs_hash=cid
		)
		"""
		policy_pubkey = UmbralPublicKey.from_bytes(bytes.fromhex(policy["policy_pubkey"]))
		alices_sig_pubkey = UmbralPublicKey.from_bytes(bytes.fromhex(policy["alice_sig_pubkey"]))
		label = policy["label"].encode()
		print("The Doctor joins policy for label '{}'".format(label.decode("utf-8")))
		doctor.join_policy(label, alices_sig_pubkey)
		dat = self.ipfs_gateway_api.cat(ipfs_hash)
		data = msgpack.loads(dat, raw=False)
		message_kits = (UmbralMessageKit.from_bytes(k) for k in data['kits'])
		data_source = Enrico.from_public_keys(
			{SigningPower: data['data_source']},
			policy_encrypting_key=policy_pubkey
		)
		message_kit = next(message_kits)
		start = timer()
		retrieved_plaintexts = doctor.retrieve(
			label=label,
			message_kit=message_kit,
			data_source=data_source,
			alice_verifying_key=alices_sig_pubkey
		)
		end = timer()
		plaintext = msgpack.loads(retrieved_plaintexts[0], raw=False)
		heart_rate = plaintext['heart_rate']
		timestamp = maya.MayaDT(plaintext['timestamp'])
		terminal_size = shutil.get_terminal_size().columns
		max_width = min(terminal_size, 120)
		columns = max_width - 12 - 27
		scale = columns / 40
		retrieval_time = "Retrieval time: {:8.2f} ms".format(1000 * (end - start))
		line = heart_rate + "   " + retrieval_time
		return line
