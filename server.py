from flask import Flask, request, send_from_directory
app = Flask(__name__)

import base64
import json
import os
import sys
from ncipfs import main
from umbral.keys import UmbralPrivateKey, UmbralPublicKey

client = main.ncipfs()

last_reader = None

DOCTOR_PUBLIC_JSON = '' #'doctor.public.json'
DOCTOR_PRIVATE_JSON = '' #'doctor.private.json'


def generate_doctor_keys():
    enc_privkey = UmbralPrivateKey.gen_key()
    sig_privkey = UmbralPrivateKey.gen_key()

    doctor_privkeys = {
        'enc': enc_privkey.to_bytes().hex(),
        'sig': sig_privkey.to_bytes().hex(),
    }

    with open(DOCTOR_PRIVATE_JSON, 'w') as f:
        json.dump(doctor_privkeys, f)

    enc_pubkey = enc_privkey.get_pubkey()
    sig_pubkey = sig_privkey.get_pubkey()
    doctor_pubkeys = {
        'enc': enc_pubkey.to_bytes().hex(),
        'sig': sig_pubkey.to_bytes().hex()
    }
    with open(DOCTOR_PUBLIC_JSON, 'w') as f:
        json.dump(doctor_pubkeys, f)


def _get_keys(file, key_class):
    if not os.path.isfile(file):
        generate_doctor_keys()

    with open(file) as f:
        stored_keys = json.load(f)
    keys = dict()
    for key_type, key_str in stored_keys.items():
        keys[key_type] = key_class.from_bytes(bytes.fromhex(key_str))
    return keys


def get_doctor_pubkeys():
    return _get_keys(DOCTOR_PUBLIC_JSON, UmbralPublicKey)


def get_doctor_privkeys():
    return _get_keys(DOCTOR_PRIVATE_JSON, UmbralPrivateKey)


## LOAD IN LOCAL FILE?
files = []
dfiles = []

def convert_to_decoded(b64):
	return base64.b64decode(b64)

def convert_to_encoded(bs):
	return base64.b64encode(bytes.fromhex(bs))

def utf8len(s):
    return len(s.encode('utf-8'))

# a route where we will display a welcome message via an HTML template
@app.route("/")
def home():  
    return send_from_directory('templates','index.html')


@app.route("/favicon.ico")
def favicon():  
    return send_from_directory('templates', "favicon.ico")

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('templates', "js/index.js")

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('templates', "css/style.css")

@app.route('/get_user_keys', methods=["GET"])
def get_user_keys():
	if DOCTOR_PUBLIC_JSON == '':
		return ""
	keys = get_doctor_pubkeys()

	payload = {
	    "enc": base64.b64encode(keys["enc"].to_bytes()).decode("utf-8"),
	    "sig": base64.b64encode(keys["sig"].to_bytes()).decode("utf-8")
	}
	print(payload)
	return json.dumps(payload)


@app.route('/connect', methods=["POST"])
def connect():
	data = request.get_json()
	client.connect(nucypher_network=data["nucypher_network"],
			  ipfs_api_gateway=data["ipfs_api_gateway"])
	print("Connect to IPFS and NUCYPHER")
	return json.dumps({"status": "Connected to networks"})

@app.route('/get_server_users', methods=["GET"])
def get_server_users():
	# data = request.get_json()
	resp = [ name for name in os.listdir("./users") if "." not in name  ]
	return json.dumps(resp)

@app.route('/get_files', methods=["GET"])
def get_files():
	# data = request.get_json()
	return json.dumps(files)

@app.route('/get_dfiles', methods=["GET"])
def get_dfiles():
	# data = request.get_json()
	return json.dumps(dfiles)

@app.route('/login_as_sender', methods=["POST"])
def login_as_sender():

	global DOCTOR_PUBLIC_JSON
	global DOCTOR_PRIVATE_JSON
	data = request.get_json()
	base = "users/"
	direco = base + data["directory"]
	# print(direco)
	client.load_user(direco)
	DOCTOR_PUBLIC_JSON =  direco + 'recipent.public.json'
	DOCTOR_PRIVATE_JSON = direco + 'recipent.private.json'
	print("Log server into local id")
	return json.dumps({"status": "Logged in as sender"})

@app.route('/add_data', methods=["POST"])
def add_data():
	global files
	data = request.get_json()
	label = data["label"]
	contents = data["contents"]

	my_label = label.encode("utf-8")
	my_contents = contents
	pubkey = client.make_key_from_label(my_label)
	cid = client.add_contents(pubkey, my_contents)
	print("Add data to IPFS network")

	entry = {
	    "name": label,
	    "type": "NA",
	    "ipfshash": cid,
	    "size": utf8len(contents),
	    "tag": "dev"
	}
	files += [entry]

	## SAVE FILES TO LOCAL FILE

	return json.dumps({"cid": cid, 
		"label": my_label.decode("utf-8"), 
		"content": my_contents 
	})

@app.route('/allow_access', methods=["POST"])
def allow_access():
	data = request.get_json()
	enc_pubkey = data["enc_pubkey"]
	sig_pubkey = data["sig_pubkey"]
	cid = data["cid"]
	label = data["label"]
	pubs = {
		'enc_pubkey': enc_pubkey.encode("utf-8"),
		'sig_pubkey': sig_pubkey.encode("utf-8"),
	}
	label = label.encode("utf-8")
	m, n = 2, 3
	policy = client.create_access_policy(
		enc_pubkey=base64.b64decode(pubs["enc_pubkey"]), 
		sig_pubkey=base64.b64decode(pubs["sig_pubkey"]), 
		label=label, 
		m=m, 
		n=n )
	to_send = [
		cid,
		convert_to_encoded(policy["policy_pubkey"]).decode("utf-8"),
		convert_to_encoded(policy["alice_sig_pubkey"]).decode("utf-8"),
		policy["label"],
	]
	print(to_send)
	print("Log server into local id")
	return json.dumps({"policy": to_send })

@app.route('/decrypt_message', methods=["POST"])
def decrypt_message():
	global last_reader
	global dfiles
	data = request.get_json()["policy"]

	priv = get_doctor_privkeys()

	doctor = client.load_recipent(
		priv["enc"],
		priv["sig"]
	)

	input_data = [data[0],data[1].encode("utf-8"),data[2].encode("utf-8"),data[3]]
	cid = input_data[0]
	policy = {
		"policy_pubkey": convert_to_decoded(input_data[1]).hex(),
		"alice_sig_pubkey": convert_to_decoded(input_data[2]).hex(),
		"label": input_data[3]
	}
	message = client.get_file_and_decrypt(doctor, policy, cid)

	dfiles +=[{
		"label": input_data[3],
		"message": message,
		"hash": cid
	}]

	print(message)
	print("Log server into reader id")
	return json.dumps({"message": message })


if __name__ == '__main__':
	# app.run(port=5000)
	if len(sys.argv) > 1:
		app.run(port=sys.argv[1])
	else:
		app.run(port=5000)