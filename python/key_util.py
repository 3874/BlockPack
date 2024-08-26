import hashlib
import base64
import nacl.signing
import nacl.utils
import nacl.signing
import nacl.encoding
import binascii

class KEY:
    
    @staticmethod
    def HexToByte(hex_str):
        if not hex_str:
            return binascii() 

        return binascii.unhexlify(hex_str)
    
    @staticmethod
    def ByteToHex(byte_string):
        return binascii.hexlify(byte_string).decode('utf-8')
    
    @staticmethod
    def StringToByte(s):
        return s.encode('utf-8')

    @staticmethod
    def MakeThash(data):
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha256(data).digest()

    @staticmethod
    def MakeKeypair():
        # 32바이트 시드를 생성
        seed = nacl.utils.random(32)
        signing_key = nacl.signing.SigningKey(seed)
        verify_key = signing_key.verify_key

        private_key = KEY.ByteToHex(seed)
        public_key = KEY.ByteToHex(verify_key.encode())

        keypair = {
            "PublicKey": public_key,
            "PrivateKey": private_key
        }

        return keypair

    @staticmethod
    def MakeAddress(public_key):
        p0 = '0x00'
        p1 = '0x6f'
        
        sha256_hash = hashlib.sha256((p0 + public_key).encode()).digest()
        s0 = base64.b64encode(sha256_hash).decode('utf-8')
        sha256_hash2 = hashlib.sha256(s0.encode())
        s1 = sha256_hash2.hexdigest()
        s2 = p1 + s1

        sha256_hash3 = hashlib.sha256(s2.encode()).digest()
        s3 = base64.b64encode(sha256_hash3).decode('utf-8')

        sha256_hash4 = hashlib.sha256(s3.encode())
        s4 = sha256_hash4.hexdigest()
        address = s2 + s4[:4]

        return address

    @staticmethod
    def MakeSignature(message, private_key_hex):

        private_key_bytes = KEY.HexToByte(private_key_hex)

        if len(private_key_bytes) != 32:
            raise ValueError("Invalid private key length, must be 32 bytes.")

        signing_key = nacl.signing.SigningKey(private_key_bytes)

        signed_message = signing_key.sign(message.encode('utf-8'))
        return KEY.ByteToHex(signed_message.signature)

    @staticmethod
    def VerifySignature(message, public_key_hex, signature_hex):

        public_key_bytes = KEY.HexToByte(public_key_hex)

        if len(public_key_bytes) != 32:
            raise ValueError("Invalid public key length, must be 32 bytes.")

        signature_bytes = binascii.unhexlify(signature_hex)
        
        if len(signature_bytes) != 64:
            raise ValueError("Invalid signature length, must be 64 bytes.")

        verify_key = nacl.signing.VerifyKey(public_key_bytes)
        
        try:
            verify_key.verify(message.encode('utf-8'), signature_bytes)
            return True
        except nacl.exceptions.BadSignatureError:
            return False