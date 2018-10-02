var base64EncodeChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
function base64encode(str) {
    var out, i, len;
    var c1, c2, c3;
    str = utf8_encode(str);
    len = str.length;
    i = 0;
    out = "";
    while (i < len) {
        c1 = str.charCodeAt(i++) & 0xff;
        if (i == len) {
            out += base64EncodeChars.charAt(c1 >> 2);
            out += base64EncodeChars.charAt((c1 & 0x3) << 4);
            out += "==";
            break;
        }
        c2 = str.charCodeAt(i++);
        if (i == len) {
            out += base64EncodeChars.charAt(c1 >> 2);
            out += base64EncodeChars.charAt(((c1 & 0x3) << 4) | ((c2 & 0xF0) >> 4));
            out += base64EncodeChars.charAt((c2 & 0xF) << 2);
            out += "=";
            break;
        }
        c3 = str.charCodeAt(i++);
        out += base64EncodeChars.charAt(c1 >> 2);
        out += base64EncodeChars.charAt(((c1 & 0x3) << 4) | ((c2 & 0xF0) >> 4));
        out += base64EncodeChars.charAt(((c2 & 0xF) << 2) | ((c3 & 0xC0) >> 6));
        out += base64EncodeChars.charAt(c3 & 0x3F);
    }
    return out;
}
function utf8_encode(str) {
    str = str.replace(/\r\n/g, "\n");
    var utftext = "";
    for (var n = 0; n < str.length; n++) {
        var c = str.charCodeAt(n);
        if (c < 128) {
            utftext += String.fromCharCode(c);
        } else if ((c > 127) && (c < 2048)) {
            utftext += String.fromCharCode((c >> 6) | 192);
            utftext += String.fromCharCode((c & 63) | 128);
        } else {
            utftext += String.fromCharCode((c >> 12) | 224);
            utftext += String.fromCharCode(((c >> 6) & 63) | 128);
            utftext += String.fromCharCode((c & 63) | 128);
        }
    }
    return utftext;
}
$(document).ready(function() {
	jQuery(document).ready(function($) {
		$("button[name='qrcode']").on('click',function() {
			if($(this).attr('data-type').indexOf("vmess")!=-1){
                	var json_obj = {"v":"","ps":"","add":"","port":"","id":"","aid":"","net":"","type":"","host":"","path":"","tls":""};
                	var json_data = $(this).attr('data-params').split(':');
                	json_obj.v = "2";
                	json_obj.add = json_data[0];
                	json_obj.port = json_data[1];
                	json_obj.id = json_data[2];
                	json_obj.aid = json_data[3];
                	json_obj.net = json_data[4];
                	json_obj.type = json_data[5];
                	str = base64encode(JSON.stringify(json_obj, undefined, 2));
			} else {
				str = base64encode($(this).attr('data-params'));
			}
			str = $(this).attr('data-type') + '://' + str;
			layer.closeAll();
			layer.open({
				type: 1,
				title: '节点自动配置信息',
				shade: [0.8, '#000'],
				skin: 'layui-layer-demo',
				offset: 'auto',
				closeBtn: 1,
				shift: 2,
				shadeClose: true,
                		content: '<div style="position: relative;  left: auto; overflow: auto; text-align: center;  margin-top: 10px; font-size: 12px;">请使用客户端扫描以下二维码</div><img style="position: relative; left: 0px; width: 240px; height: 240px; top: 0px;" src="https://api.npist.com/qrcode/qrcodeapi.php?w=2&text='+ str +'" /><div style="position: relative;  left: auto; overflow: auto; text-align: center; margin-top: 10px; font-size: 12px;">或复制以下链接导入客户端</div><div style="position: relative;  left: auto; overflow: auto; text-align: center; margin: 10px 10px 10px 10px; font-size: 12px;"><input type="text" name="lastname" id="inputLastName" value="' + str + '" class="form-control" /></div>'
			});
		});
	});
});
