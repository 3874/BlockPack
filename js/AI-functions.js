var AISA = AISA || {};

AISA.Net = [
    {'host':'https://api.quickreview.company'},
    {'host':'localhost'},
];

function SignOut() {
    localStorage.removeItem("mykey");
    location.href = "./sign-in.html?";
};

function CheckSignIn(addr) {
    var html_txt ="";
    if (!addr) {
        html_txt += "<a class=\"offcanvas-toggler active custom-dropdown-toggler\" href=\"./sign-in.html?\" >";
        html_txt += "<i class=\"mdi mdi-account icon\"></i>Sign-in";
        html_txt += "</a>";
   
        $("#sign-in-btn").html(html_txt);
        $("#sign-in-btn").attr("class", "custom-dropdown");

    }; 
};


/** request를 이용하여 validation 체크 함수들 */

function VerifyKEY() {
    try {
        var now = new Date().getTime();
        var future = now + 1000;
        var myKey = GetMyKey();
        
        if (!myKey) {
            throw new Error("Unable to retrieve key information.");
        }
        
        var requests = JSON.stringify({
            'type': 'VerifyKEY',
            'version': '1.0.0.0',
            'address': myKey.address,
            'timestamp': parseInt(future + '000'),
        });
        
        return Request(requests);
    } catch (error) {
        console.error("An error occurred in VerifyKEY:", error);
        return null; // or handle the error in an appropriate way
    }
};


function VerifyID() {
    try {
        var now = new Date().getTime();        
        var future = now + 1000;
        var requests = JSON.stringify({
            'type': 'VerifyID',
            'version': '1.0.0.0',
            'address': GetMyKey().address,
            'timestamp': parseInt(future + '000'),
        });
        return Request(requests);
    } catch (error) {
        console.error("An error occurred while verifying ID:", error);
        return null; // or any appropriate action you want to take in case of an error
    }
};

function GetTransactions() {
    try {
        var now = new Date().getTime();        
        var future = now + 1000;
        var requests = JSON.stringify({
            'type': 'GetTransactions',
            'version': '1.0.0.0',
            'address': GetMyKey().address,
            'timestamp': parseInt(future + '000'),
        });
        return Request(requests);
    } catch (error) {
        console.error("GetTransactions 함수에서 예외 발생:", error);
        return null;
    }
};


function DeleteFile(info) {
    try {
        if (!info) {
            throw new Error('Info is required for deleting file.');
        }

        var now = new Date().getTime();        
        var future = now + 1000;
        var transaction = JSON.stringify({
            'type': 'DeleteFileFromS3',
            'version': '1.0.0.0',
            'address': GetMyKey().address,
            'timestamp': parseInt(future + '000'),
            'payload': info,
        });
        Transaction(transaction);
    } catch (error) {
        console.error('Error occurred while deleting file:', error.message);
        // 예외 처리 추가 동작을 여기에 추가할 수 있습니다.
    }
};

/** Request와 Transaction 기초 함수 */

async function Request(payload) {

    var thash = KEY.MakeThash(payload);
    var signature = KEY.MakeSignature(thash, GetMyKey().private_key, GetMyKey().public_key);

    var result;

    $.ajax({
        type:'post',   //post 방식으로 전송
        url: host + '/request',   //데이터를 주고받을 파일 주소
        contentType: "application/x-www-form-urlencoded; charset=UTF-8",
        data: {
            'request': payload,
            'thash': thash,
            'public_key': GetMyKey().public_key,
            'signature': signature
        },
        dataType:'json',   
        async: false,   //json 파일 형식으로 값을 담아온다.
        success : function(data){   
            result = data;
        },
        error : function(xhr, textStatus, errorThrown) {     // 실패 시
            if(xhr.status === 0) {
                result = "네트워크 연결이 끊어졌습니다.";
            } else if(xhr.status == 404) {
                result = "요청된 페이지를 찾을 수 없습니다.";
            } else if(xhr.status == 500) {
                result = "내부 서버 오류가 발생했습니다.";
            } else {
                result = "오류 발생: " + errorThrown;
            }
        }
    });

    return result;
};


async function Transaction(transaction) {
    var thash = KEY.MakeThash(transaction);
    var signature = KEY.MakeSignature(thash, GetMyKey().private_key, GetMyKey().public_key);
    var rss = {};

    $.ajax({
        type: 'post',
        url: host + '/transaction',
        contentType: "application/x-www-form-urlencoded; charset=UTF-8",
        data: {
            'transaction': transaction,
            'thash': thash,
            'public_key': GetMyKey().public_key,
            'signature': signature
        },
        dataType: 'json',
        async: false,
        success: function(data) {
            rss = data;
        },
        error: function(xhr, status, error) {
            // 오류가 발생하면 이 부분이 실행됩니다.
            console.error("Ajax 오류 발생:", status, error);
            // 오류 처리를 위해 rss 객체를 설정합니다.
            rss = {
                error: "Ajax 오류 발생: " + status + " - " + error
            };
        },
        complete: function(xhr, status) {
            // Ajax 요청이 완료되면 이 부분이 실행됩니다.
            console.log("Ajax 요청 완료:", status);
        }
    });

    return rss;
};


function UploadingImage(files) {
    var form = new FormData();
    var result; 

    form.append("image", files[0]);

    $.ajax({
        type:'post',   //post 방식으로 전송
        url: host + '/UploadImage',   //데이터를 주고받을 파일 주소
        data: form,
        dataType:'json',
        contentType: false,
        processData: false,   
        async: false,   //json 파일 형식으로 값을 담아온다.
        success : function(data){   //파일 주고받기가 성공했을 경우
            data['result'] = 's';
            result = data;
        },
        error : function(err) {     // 실패 시
            err['result'] = 'f';
            result = err;            
        }
    });
    return result;
};

function Download_Key() {
    var json_key = localStorage.getItem("mykey");
    var tmpkey = JSON.parse(json_key);

    json_key = JSON.stringify(tmpkey);

    download("mykey.txt", json_key);       
    localStorage.setItem("mykey",json_key);
      
 };

 function download(filename, text) {
    var pom = document.createElement('a');
    pom.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    pom.setAttribute('download', filename);

    if (document.createEvent) {
        var event = document.createEvent('MouseEvents');
        event.initEvent('click', true, true);
        pom.dispatchEvent(event);
    }
    else {
        pom.click();
    }
};

function sendSns(sns, url, txt)
{
    var o;
    var _url = encodeURIComponent(url);
    var _txt = encodeURIComponent(txt);
    var _br  = encodeURIComponent('\r\n');

    switch(sns)
    {
        case 'facebook':
            o = {
                method:'popup',
                url:'http://www.facebook.com/sharer/sharer.php?u=' + _url
            };
            break;

        case 'twitter':
            o = {
                method:'popup',
                url:'https://twitter.com/intent/tweet?text=' + _txt + '&url=' + _url
            };

            break;

        case 'wechat':
            o = {
                method:'web2app',
                url:'weixin://dl/chat?{toID}' + _url
            };

            break;

        case 'whatsapp':
            o = {
                method:'popup',
                url:'https://wa.me?text=' + _txt + '&url=' + _url
            };

            break;

        case 'email':
            o = {
                method:'popup',
                url:'mailto:?subject=' + _txt + '&body=' + _url
            };

            break;

         case 'kakaotalk':
            o = {
                method:'web2app',
                param:'sendurl?msg=' + _txt + '&url=' + _url + '&type=link&apiver=2.0.1&appver=2.0&appid=dev.epiloum.net&appname=' + encodeURIComponent('Epiloum 개발노트'),
                a_store:'itms-apps://itunes.apple.com/app/id362057947?mt=8',
                g_store:'market://details?id=com.kakao.talk',
                a_proto:'kakaolink://',
                g_proto:'scheme=kakaolink;package=com.kakao.talk'
            };

            break; 

        default:
            alert('No supporting SNS.');
            return false;

    }
 
    switch(o.method)
    {
        case 'popup':
            window.open(o.url);
            break; 

        case 'web2app':
            if(navigator.userAgent.match(/android/i))
            {
                // Android
                setTimeout(function(){ location.href = 'intent://' + o.param + '#Intent;' + o.g_proto + ';end'}, 100);
            }

            else if(navigator.userAgent.match(/(iphone)|(ipod)|(ipad)/i))
            {
                // Apple
                setTimeout(function(){ location.href = o.a_store; }, 200);         
                setTimeout(function(){ location.href = o.a_proto + o.param }, 100);
            }

            else
            {
                alert('This function is available in Mobile Phone.');
            }

            break;
    }

};



