const host = 'http://localhost:9000';

async function communicate(endpoint, payload, PrivateKey, PublicKey) {
    const thash = KEY.MakeThash(payload);
    const signature = KEY.MakeSignature(thash, PrivateKey, PublicKey);
    let result = null;

    try {
        result = await $.ajax({
            type: 'POST',
            url: `${host}/${endpoint}`,
            contentType: "application/json; charset=UTF-8",
            data: JSON.stringify({
                ...(endpoint === 'requests' ? {'requests': payload} : {'transactions': payload}),
                'public_key': PublicKey,
                'signature': signature,
            }),
            dataType: 'json'
        });
    } catch (xhr) {
        if (xhr.status === 0) {
            return "네트워크 연결이 끊어졌습니다.";
        } else if (xhr.status === 404) {
            return "요청된 페이지를 찾을 수 없습니다.";
        } else if (xhr.status === 500) {
            return "내부 서버 오류가 발생했습니다.";
        } else {
            return "오류 발생: " + xhr.statusText;
        }
    }

    return result;
}

async function Request(payload, PrivateKey, PublicKey) {
    return await communicate('requests', payload, PrivateKey, PublicKey);
}

async function Transaction(payload, PrivateKey, PublicKey) {
    return await communicate('transactions', payload, PrivateKey, PublicKey);
}