<?php
 /*
 * @package    V2rayMS_ClientAPI
 * @author     Npist <npist35@gmail.com>
 * @license    http://opensource.org/licenses/MIT The MIT License
 * @version    0.1.1
 * @link       https://npist.com/
 */

 /*
 * API接口为客户端开发做准备
 * 配合WHMCS及V2rayMS使用，前端插件不限(不修改数据库结构即可)
 * 调用WHMCS LocalAPI及Capsule::table进行数据获取
 * 使用POST接受客户端信息,RSA加密通讯
 * 转载修改及其他用途请署名
 */
if ($_SERVER['HTTP_USER_AGENT'] != 'V2rayMS_Client/API0.1') {
    exit();
};

require("init.php");
use WHMCS\Database\Capsule;

// WHMCS管理员账户名
$admin_username = '';
// RSA私钥(不要使用私钥密码 或 修改解密模块源代码)
$private_key = '';
// RSA公钥
$public_key = '';

$postdata = file_get_contents("php://input");

function decrypt_data($data)
{
    try {
        global $private_key;
        $bytes_str = base64_decode($data);
        $pi_key = openssl_pkey_get_private($private_key);
        openssl_private_decrypt($bytes_str, $decrypted, $pi_key);
        return $decrypted;
    } catch (Exception $e) {
        echo json_encode(array("error_code", "0x050"));
        exit();
    }

}
function encrypt_data($data)
{
    try {
        global $public_key;
        openssl_public_encrypt($data, $encrypted, $public_key);
        $encrypted = base64_encode($encrypted);
        return $encrypted;
    } catch (Exception $e) {
        echo json_encode(array("error_code", "0x051"));
        exit();
    }

}
function GetClientID($clientname, $clientpassword)
{
    global $admin_username;
    $command = 'ValidateLogin';
    $postData = array(
        'email' => $clientname,
        'password2' => $clientpassword,
    );
    $results = localAPI($command, $postData, $admin_username);
    if ($results["result"] == 'error') {
        return array("error_code", "0x010");
    } elseif ($results["result"] == 'success') {
        // $value = array(
        //     "clientid" => $results["userid"]
        // );
        if (is_int($results["userid"])) {
            return $results["userid"];
        } else {
        echo json_encode(array("error_code", "0x013"));
        exit();
        }
    } else {
        echo json_encode(array("error_code", "0x011"));
        exit();
    }
}
function GetClientsProductsByUser($clientid)
{
    global $admin_username;
    $command = 'GetClientsProducts';
    $postData = array(
        'clientid' => $clientid,
        'stats' => true,
    );
    $results = localAPI($command, $postData, $admin_username);
    if ($results["result"] == "success") {
        return $results;
    } else {
        echo json_encode(array("error_code", "0x032"));
        exit();
    }
}
function GetClientsProductsByOrderId($productid)
{
    global $admin_username;
    $command = 'GetOrders';
    $postData = array(
        'id' => $productid,
    );
    $results = localAPI($command, $postData, $admin_username);
    if ($results["result"] == "success") {
        return $results;
    } else {
        echo json_encode(array("error_code", "0x031"));
        exit();
    }
}
function GetClientsProductConfigure($serverid, $param)
{
    try {
        $results = Capsule::table('tblproducts')
            ->where('id', $serverid)
            ->select($param)
            ->get();
        return json_decode(json_encode($results[0]), true)[$param];
    } catch (Exception $e) {
        echo json_encode(array("error_code", "0x020"));
        exit();
    }
}
function GetServerConnectConfigure($serverid)
{
    try {
        $results = Capsule::table('tblservers')
            ->where('id', $serverid)
            ->select('username', 'password', 'ipaddress')
            ->get();
        $results2 = json_decode(json_encode($results[0]), true);
        $results2["password"] = DecryptWhmcsPassword($results2['password']);
        return $results2;
    } catch (Exception $e) {
        echo json_encode(array("error_code", "0x021"));
        exit();
    }
}
function DecryptWhmcsPassword($encryptedpassword)
{
    global $admin_username;
    $command = 'DecryptPassword';
    $postData = array(
        'password2' => $encryptedpassword,
    );
    $results = localAPI($command, $postData, $admin_username);
    if ($results["result"] == "success") {
        return $results["password"];
    } else {
        echo json_encode(array("error_code", "0x030"));
        exit();
    }
}

$data = json_decode(decrypt_data($postdata), true);

if (isset($data["username"]) and isset($data["password"])) {
    $clientid = GetClientID($data["username"], $data["password"]);
    $user_product = GetClientsProductsByUser($clientid)["products"]["product"];
    $order_num = sizeof($user_product);
    $All_Order_information = array();
    while ($order_num > 0) {
        $order_raw_information = $user_product[$order_num - 1];
        $order_information = array(
            "name" => $order_raw_information["name"],
            "orderid" => $order_raw_information["orderid"],
            "serverid" => $order_raw_information["serverid"],
            // "productid" => $order_raw_information["id"],
            "nextduedate" => $order_raw_information["nextduedate"],
            "status" => $order_raw_information["status"],
        );
        array_push($All_Order_information, $order_information);
        $order_num -= 1;
    }
    $encrypted = encrypt_data(json_encode($All_Order_information));
    echo $encrypted;
} elseif (isset($data["username"]) and isset($data["orderid"]) and isset($data["serverid"])) {
    $service_id = GetClientsProductsByOrderId($data["orderid"])["orders"]["order"][0]["lineitems"]["lineitem"][0]["relid"];
    $server_id = $data["serverid"];
    $v2ray_connect = GetClientsProductConfigure($server_id, 'configoption4');
    $v2ray_database = GetServerConnectConfigure($server_id);
    $v2ray_database_table = GetClientsProductConfigure($server_id, 'configoption1');
    try {
        $databasehost = $v2ray_database['ipaddress'];
        $databasename = $v2ray_database_table;
        $databaseuser = $v2ray_database['username'];
        $databasepass = $v2ray_database['password'];
        $database = new PDO('mysql:host=' . $databasehost . ';dbname=' . $databasename, $databaseuser, $databasepass);
        $usage = $database
            ->prepare(
                'SELECT `id`,`uuid`,`usetime`,`uplink`,`downlink`,`transfer_enable`,`enable`,`created_at`,`updated_at`,`sid` FROM `user` WHERE `sid` = :sid'
            );
        $usage->bindValue(':sid', $service_id);
        $usage->execute();
        $usage = $usage->fetch();
        $ReturnValue = array(
            'orderid' => $data['orderid'],
            'server_conn' => $v2ray_connect,
            'uuid' => $usage['uuid'],
            'u' => $usage['uplink'],
            'd' => $usage['downlink'],
            't' => $usage['transfer_enable']
        );
        $encrypted = encrypt_data(json_encode($ReturnValue));
        echo $encrypted;
    } catch (PDOException $e) {
        echo json_encode(array("error_code", "0x033"));
        exit();
    }
}
