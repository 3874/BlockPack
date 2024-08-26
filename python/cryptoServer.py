from key_util import KEY
from flask import Flask, request, jsonify, send_from_directory, json
from tinydb import TinyDB
from flask_cors import CORS
import logging
import os, sys

qr_app = Flask(__name__)
CORS(qr_app)

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

@qr_app.route('/checkSum')
def checkSum():

    keypair = KEY.MakeKeypair()
    address = KEY.MakeAddress(keypair['PublicKey'])
    sigNa = KEY.MakeSignature('hello', keypair['PrivateKey'])
    res = KEY.VerifySignature('hello', keypair['PublicKey'], sigNa)
    
    return {'keypair':keypair, 'address':address, 'signature':sigNa, 'verify':res}

@qr_app.route('/verify', methods=['POST'])
def verify():
    payload = request.get_json()  # JSON 요청 몸체 가져오기

    signature = payload['signature']
    publicKey = payload['publicKey']
    message = payload['message']
    
    res = KEY.VerifySignature(message, publicKey, signature)
    
    if res:
        return jsonify({"result": "success"})
    else:
        return jsonify({"result": "fail"})

@qr_app.route('/file/<corpID>', methods=['GET'])
def get_files_by_corp_id(corpID):

    files = FundTable.all()

    matching_files = []
    for file in files:
        if file.get('company_code') == corpID: 
            matching_files.append({'doc_id': file.doc_id, 'file_name': file['file_name']})

    if not matching_files:
        return jsonify({"error": "No matched files"}), 404

    return jsonify({"files": matching_files}), 200


@qr_app.route('/upload', methods=['POST'])
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

@qr_app.route('/delete', methods=['DELETE'])
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

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'xls', 'xlsx', 'doc', 'docx', 'ppt', 'pptx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def image_file(filename):
    IMAGE_EXTENTIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in IMAGE_EXTENTIONS

if __name__ == '__main__':
    qr_app.run(host='0.0.0.0', port=cport, debug=True)