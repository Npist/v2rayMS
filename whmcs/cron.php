<?php
//读取数据库连接信息
$json_string = file_get_contents(__DIR__ . '/sqlconn.json');
$data = json_decode($json_string, true);
//连接数据库
try {
	$sql = new PDO("mysql:host=" . $data['host'] . ";port=" . strval($data['port']) . ";dbname=" . $data['db'], $data['user'], $data['password']);
	$sql -> setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
	die ("错误: " . $e->getMessage() . "\n");
}
die("成功: 连接数据库。" . "\n");
$sql -> exec("set names utf8");
//执行重置流量语句
try {
    $sql_results  = $sql -> query("UPDATE user SET uplink=0 , downlink=0 , updated_at=" . time() . " WHERE need_reset=1");
	die ("成功: 重置了" . $sql_results->rowCount() . "个用户的流量。" . "\n");
} catch (PDOException $e) {
    die ("错误: " . $e->getMessage() . "\n");
}
?>
