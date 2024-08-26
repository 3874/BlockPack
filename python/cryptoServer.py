from key_util import KEY
from flask import Flask, request, jsonify, send_from_directory, json
from tinydb import TinyDB
from flask_cors import CORS
import logging
import os, sys

qr_app = Flask(__name__)
CORS(qr_app)

VERSION = '0.0.1'
cport = 9000

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'template')
DB_FOLDER = os.path.join(BASE_DIR, 'db')

if not os.path.exists(TEMPLATE_FOLDER):
    os.makedirs(TEMPLATE_FOLDER)
    
if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)

db_path = os.path.join(DB_FOLDER,'ledger.json')
db = TinyDB(db_path)
FundTable = db.table('MoneyTable')
    

@qr_app.route('/home')
def home():
    return send_from_directory(TEMPLATE_FOLDER, 'index.html')

@qr_app.route('/requests', methods=['POST'])
def requests():
    trdata = request.get_json()

    if not trdata:
        return jsonify({"error": "Invalid JSON"}), 400

    checkRes = checkValidation('requests', trdata)
    
    if not checkRes:
        return jsonify({"result": "fail"})

    payload = trdata['requests']
    Parsingpayload = json.loads(payload)
    process = Parsingpayload['process']
    address = Parsingpayload['address']

    if process == 'verify':
        return jsonify({'result':checkRes})
    elif process == 'checkSum':
        return checkSum()
    elif process == 'file':
        return get_files()
    else:
        return 'Nothing'
    
@qr_app.route('/transactions', methods=['POST'])
def transactions():
    trdata = request.get_json()

    if not trdata:
        return jsonify({"error": "Invalid JSON"}), 400
    
    checkRes = checkValidation('transactions', trdata)
    
    if not checkRes:
        return jsonify({"result": "fail"})

    payload = trdata['transactions']
    Parsingpayload = json.loads(payload)
    process = Parsingpayload['process']
    address = Parsingpayload['address']

    if process == 'upload':
        return upload_file()
    elif process == 'delete':
        return delete_file()
    else:
        return 'Nothing'

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'xls', 'xlsx', 'doc', 'docx', 'ppt', 'pptx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def image_file(filename):
    IMAGE_EXTENTIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in IMAGE_EXTENTIONS

def checkSum():
    keypair = KEY.MakeKeypair()
    address = KEY.MakeAddress(keypair['PublicKey'])
    sigNa = KEY.MakeSignature('hello', keypair['PrivateKey'])
    res = KEY.VerifySignature('hello', keypair['PublicKey'], sigNa)
    
    return {'keypair':keypair, 'address':address, 'signature':sigNa, 'verify':res}

def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
      
    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400
    
    file_path = os.path.join(TEMPLATE_FOLDER, file.filename)
    
    if os.path.exists(file_path):
        return jsonify({"error": "File already exists"}), 400

    try:
        file.save(file_path)
        FundTable.insert({'file_name': file.filename, 'tags':[], 'summary':'', 'location': file_path})
        return jsonify({"success": "File uploaded", "filename": file.filename}), 201
    except Exception as e:
        logging.error(f"Error saving file: {e}")
        return jsonify({"error": "File could not be saved"}), 500

def delete_file():
    doc_id = request.args.get('doc_id', type=int)
    if doc_id is None:
        return jsonify({"error": "No doc_id provided"}), 400

    file_entry = FundTable.get(doc_id=doc_id)

    if not file_entry:
        return jsonify({"error": "File not found"}), 404

    try:
        file_path = file_entry['location']
        FundTable.remove(doc_ids=[doc_id])
        os.remove(file_path)
        return jsonify({"success": "File deleted", "doc_id": doc_id}), 200
    except Exception as e:
        logging.error(f"Error deleting file: {e}")
        return jsonify({"error": "File could not be deleted"}), 500

def get_files():

    files = FundTable.all()

    return jsonify({"files": files}), 200

def checkValidation(com, trdata):

    if com not in trdata:
        return False
        
    payload = trdata[com]
    Parsingpayload = json.loads(payload)
    
    if 'version' not in Parsingpayload:
        return False
    
    if Parsingpayload['version'] != VERSION:
        return False

    thash = KEY.MakeThash(payload)
    signature = trdata.get('signature')
    publicKey = trdata.get('public_key')

    if not signature or not publicKey:
        return False

    res = KEY.VerifySignature(thash, publicKey, signature)
    
    return res

if __name__ == '__main__':
    qr_app.run(host='0.0.0.0', port=cport, debug=True)