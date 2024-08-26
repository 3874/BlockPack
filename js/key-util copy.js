var KEY = KEY || {};

KEY.HexToByte = function (str) {
    if (!str) {
        return new Uint8Array();
    }

    var a = [];
    for (var i = 0, len = str.length; i < len; i += 2) {
        a.push(parseInt(str.substr(i, 2), 16));
    }

    return new Uint8Array(a);
};

KEY.ByteToHex = function (byte) {
    if (!byte) {
        return '';
    }

    var hexStr = '';
    for (var i = 0; i < byte.length; i++) {
        var hex = (byte[i] & 0xff).toString(16);
        hex = (hex.length === 1) ? '0' + hex : hex;
        hexStr += hex;
    }

    return hexStr.toLowerCase();
};

KEY.StringToByte = function (str) {
    var buf = new Uint8Array(new ArrayBuffer(str.length));
    for (var i = 0, strLen = str.length; i < strLen; i++) {
        buf[i] = str.charCodeAt(i);
    }
    return buf;
};

KEY.MakeThash = function (str) {
    if (typeof str !== 'string') {
        str = JSON.stringify(str);
    }

    return CryptoJS.SHA256(str).toString(CryptoJS.enc.Base64);
};

KEY.MakeKeypair = function () {
    var keypair = nacl.sign.keyPair();
    var private_key = this.ByteToHex(keypair.secretKey).substring(0, 64);
    var public_key = this.ByteToHex(keypair.publicKey);

    keypair = {
        PublicKey: public_key,
        PrivateKey: private_key,
    };

    return keypair;
};

KEY.MakeAddress = function (public_key) {
    var p0 = '0x00';
    var p1 = '0x6f';
    var address, s0, s1, s2;

    s0 = CryptoJS.SHA256(p0 + public_key).toString(CryptoJS.enc.Base64);
    s0 = CryptoJS.SHA256(s0).toString(CryptoJS.enc.Hex);
    s1 = p1 + s0;
    s2 = CryptoJS.SHA256(s1).toString(CryptoJS.enc.Base64);
    s2 = CryptoJS.SHA256(s2).toString(CryptoJS.enc.Hex);

    address = s1.substring(0, 56) + s2.substring(0, 4);
    
    return address;
};

KEY.MakeSignature = function (str, private_key, public_key) {
    private_key = private_key + public_key;

    return this.ByteToHex(nacl.sign.detached(this.StringToByte(str), this.HexToByte(private_key)));
};

KEY.ValidSignature = function (str, public_key, signature) {
    return nacl.sign.detached.verify(this.StringToByte(str), this.HexToByte(signature), this.HexToByte(public_key));
};

