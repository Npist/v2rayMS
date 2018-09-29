<?php
function initializesql(array $params)
{
	$query['CREATE_ACCOUNT'] = 'INSERT INTO `user`(`uuid`,`uplink`,`downlink`,`transfer_enable`,`created_at`,`updated_at`,`need_reset`,`sid`) VALUES (:uuid,0,0,:transfer_enable,UNIX_TIMESTAMP(),0,:need_reset,:sid)';
	$query['ALREADY_EXISTS'] = 'SELECT `uuid` FROM `user` WHERE `sid` = :sid';
	$query['ENABLE'] = 'UPDATE `user` SET `enable` = :enable WHERE `sid` = :sid';
	$query['DELETE_ACCOUNT'] = 'DELETE FROM `user` WHERE `sid` = :sid';
	$query['CHANGE_PASSWORD'] = 'UPDATE `user` SET uuid = :uuid WHERE `sid` = :sid';
	$query['USERINFO'] = 'SELECT `id`,`uuid`,`usetime`,`uplink`,`downlink`,`transfer_enable`,`enable`,`created_at`,`updated_at`,`need_reset`,`sid` FROM `user` WHERE `sid` = :sid';
	$query['RESET'] = 'UPDATE `user` SET `uplink` = 0,`downlink` = 0 WHERE `sid` = :sid';
	$query['CHANGE_PACKAGE'] = 'UPDATE `user` SET `transfer_enable` = :transfer_enable WHERE `sid` = :sid';
	return $query;
}
function uuid($prefix = '')
{
	$chars = md5(uniqid(mt_rand(), true));
	$uuid  = substr($chars,0,8) . '-';
	$uuid .= substr($chars,8,4) . '-';
	$uuid .= substr($chars,12,4) . '-';
	$uuid .= substr($chars,16,4) . '-';
	$uuid .= substr($chars,20,12);
	return $prefix . $uuid;
}
function convert_tran($number, $from, $to)
{
	$to = strtolower($to);
	$from = strtolower($from);
	switch ($from) {
	case 'gb':
		switch ($to) {
		case 'mb':
			return $number * 1024;
		case 'bytes':
			return $number * 1073741824;
		default:
		}
		return $number;
		break;
	case 'mb':
		switch ($to) {
		case 'gb':
			return $number / 1024;
		case 'bytes':
			return $number * 1048576;
		default:
		}
		return $number;
		break;
	case 'bytes':
		switch ($to) {
		case 'gb':
			return $number / 1073741824;
		case 'mb':
			return $number / 1048576;
		default:
		}
		return $number;
		break;
	default:
	}
	return $number;
}
function _MetaData()
{
	return array('DisplayName' => 'V2rayMS for WHMCS', 'RequiresServer' => true);
}
function V2rayMS_ConfigOptions()
{
	return array(
	'数据库名' => array('Type' => 'text', 'Size' => '25'),
	'重置流量' => array(
		'Type'        => 'dropdown',
		'Options'     => array('1' => '需要重置', '0' => '不需要重置'),
		'Description' => '是否需要重置流量'
		),
	'流量限制' => array('Type' => 'text', 'Size' => '25', 'Description' => '单位MB'),
	'线路列表' => array('Type' => 'textarea', 'Rows' => '3', 'Cols' => '50', 'Description' => '格式:线路名称|服务器地址|端口|AlterID|传输协议|伪装混淆| 一行一个')
	);
}
function V2rayMS_TestConnection(array $params)
{
	try {
		$dbhost = $params['serverip'];
		$dbuser = $params['serverusername'];
		$dbpass = $params['serverpassword'];
		$db = new PDO('mysql:host=' . $dbhost, $dbuser, $dbpass);
		$success = true;
		$errorMsg = '';
	}
	catch (Exception $e) {
		logModuleCall('V2rayMS', 'V2rayMS_TestConnection', $params, $e->getMessage(), $e->getTraceAsString());
		$success = false;
		$errorMsg = $e->getMessage();
	}
	return array('success' => $success, 'error' => $errorMsg);
}
function V2rayMS_CreateAccount(array $params)
{
	$query = initializesql($params);
	try {
		$dbhost = $params['serverip'];
		$dbname = $params['configoption1'];
		$dbuser = $params['serverusername'];
		$dbpass = $params['serverpassword'];
		$db = new PDO('mysql:host=' . $dbhost . ';dbname=' . $dbname, $dbuser, $dbpass);
		$already = $db->prepare($query['ALREADY_EXISTS']);
		$already->bindValue(':sid', $params['serviceid']);
		$already->execute();
		if ($already->fetchColumn()) {
			return 'User already exists.';
		}
		$bandwidth = (!empty($params['configoption3']) ? convert_tran($params['configoption3'], 'mb', 'bytes') : (!empty($params['configoptions']['traffic']) ? convert_tran($params['configoptions']['traffic'], 'gb', 'bytes') : '1099511627776'));
		$create = $db->prepare($query['CREATE_ACCOUNT']);
		$create->bindValue(':uuid', uuid());
		$create->bindValue(':transfer_enable', $bandwidth);
		$create->bindValue(':need_reset', $params['configoption2']);
		$create->bindValue(':sid', $params['serviceid']);
		$create = $create->execute();

		if ($create) {
			return 'success';
			}
		else {
			$error = $db->errorInfo();
			return $error;
		}
	}
	catch (Exception $e) {
		logModuleCall('V2rayMS', 'V2rayMS_CreateAccount', $params, $e->getMessage(), $e->getTraceAsString());
		return $e->getMessage();
	}
}
function V2rayMS_SuspendAccount(array $params)
{
	$query = initializesql($params);
	try {
		$dbhost = $params['serverip'];
		$dbname = $params['configoption1'];
		$dbuser = $params['serverusername'];
		$dbpass = $params['serverpassword'];
		$db = new PDO('mysql:host=' . $dbhost . ';dbname=' . $dbname, $dbuser, $dbpass);
		$enable = $db->prepare($query['ENABLE']);
		$enable->bindValue(':enable', '0');
		$enable->bindValue(':sid', $params['serviceid']);
		
		$todo = $enable->execute();
		if (!$todo) {
			$error = $db->errorInfo();
			return $error;
		}
		return 'success';
	}
	catch (Exception $e) {
		logModuleCall('V2rayMS', 'V2rayMS_SuspendAccount', $params, $e->getMessage(), $e->getTraceAsString());
		return $e->getMessage();
	}
}
function V2rayMS_UnsuspendAccount(array $params)
{
	$query = initializesql($params);
	try {
		$dbhost = $params['serverip'];
		$dbname = $params['configoption1'];
		$dbuser = $params['serverusername'];
		$dbpass = $params['serverpassword'];
		$db = new PDO('mysql:host=' . $dbhost . ';dbname=' . $dbname, $dbuser, $dbpass);
		$enable = $db->prepare($query['ENABLE']);
		$enable->bindValue(':enable', '1');
		$enable->bindValue(':sid', $params['serviceid']);
		
		$todo = $enable->execute();
		if (!$todo) {
			$error = $db->errorInfo();
			return $error;
		}
		return 'success';
	}
	catch (Exception $e) {
		logModuleCall('V2rayMS', 'V2rayMS_UnsuspendAccount', $params, $e->getMessage(), $e->getTraceAsString());
		return $e->getMessage();
	}
}
function V2rayMS_TerminateAccount(array $params)
{
	$query = initializesql($params);
	try {
		$dbhost = $params['serverip'];
		$dbname = $params['configoption1'];
		$dbuser = $params['serverusername'];
		$dbpass = $params['serverpassword'];
		$db = new PDO('mysql:host=' . $dbhost . ';dbname=' . $dbname, $dbuser, $dbpass);
		$already = $db->prepare($query['ALREADY_EXISTS']);
		$already->bindValue(':sid', $params['serviceid']);
		$already->execute();
		$already = $already->fetch();
		if ($already) {	
		}
		else {
			return 'User does not exists.';
		}
		$enable = $db->prepare($query['DELETE_ACCOUNT']);
		$enable->bindValue(':sid', $params['serviceid']);
		
		$todo = $enable->execute();
		if (!$todo) {
			$error = $db->errorInfo();
			return $error;
		}
		return 'success';
	}
	catch (Exception $e) {
		logModuleCall('V2rayMS', 'V2rayMS_TerminateAccount', $params, $e->getMessage(), $e->getTraceAsString());
		return $e->getMessage();
	}
}
function V2rayMS_ChangePackage(array $params)
{
	$query = initializesql($params);
	try {
		$dbhost = $params['serverip'];
		$dbname = $params['configoption1'];
		$dbuser = $params['serverusername'];
		$dbpass = $params['serverpassword'];
		$db = new PDO('mysql:host=' . $dbhost . ';dbname=' . $dbname, $dbuser, $dbpass);
		$bandwidth = (!empty($params['configoption3']) ? convert_tran($params['configoption3'], 'mb', 'bytes') : (!empty($params['configoptions']['traffic']) ? convert_tran($params['configoptions']['traffic'], 'gb', 'bytes') : '1099511627776'));
		$enable = $db->prepare($query['CHANGE_PACKAGE']);
		$enable->bindValue(':transfer_enable', $bandwidth);
		$enable->bindValue(':sid', $params['serviceid']);
		$todo = $enable->execute();
		if (!$todo) {
			$error = $db->errorInfo();
			return $error;
		}
		return 'success';
	}
	catch (Exception $e) {
		logModuleCall('V2rayMS', 'V2rayMS_ChangePackage', $params, $e->getMessage(), $e->getTraceAsString());
		return $e->getMessage();
	}
}
function V2rayMS_ChangePassword(array $params)
{
	$query = initializesql($params);
	try {
		$dbhost = $params['serverip'];
		$dbname = $params['configoption1'];
		$dbuser = $params['serverusername'];
		$dbpass = $params['serverpassword'];
		$db = new PDO('mysql:host=' . $dbhost . ';dbname=' . $dbname, $dbuser, $dbpass);
		$enable = $db->prepare($query['CHANGE_PASSWORD']);
		$enable->bindValue(':uuid', uuid());
		$enable->bindValue(':sid', $params['serviceid']);
		$todo = $enable->execute();
		if (!$todo) {
			$error = $db->errorInfo();
			return $error;
		}
		return 'success';
	}
	catch (Exception $e) {
		logModuleCall('V2rayMS', 'V2rayMS_ChangePassword', $params, $e->getMessage(), $e->getTraceAsString());
		return $e->getMessage();
	}
}
function V2rayMS_AdminCustomButtonArray()
{
	return array('Reset' => 'ResetBandwidth');
}
function V2rayMS_ResetBandwidth(array $params)
{
	$query = initializesql($params);
	try {
		$dbhost = ($params['serverip']);
		$dbname = ($params['configoption1']);
		$dbuser = ($params['serverusername']);
		$dbpass = ($params['serverpassword']);
		$db = new PDO('mysql:host=' . $dbhost . ';dbname=' . $dbname, $dbuser, $dbpass);
		$enable = $db->prepare($query['RESET']);
		$enable->bindValue(':sid', $params['serviceid']);
		$todo = $enable->execute();
		if (!$todo) {
			$error = $db->errorInfo();
			return $error;
		}
		return 'success';
	}
	catch (Exception $e) {
		logModuleCall('V2rayMS', 'V2rayMS_ResetBandwidth', $params, $e->getMessage(), $e->getTraceAsString());
		return $e->getMessage();
	}
}
function V2rayMS_ClientArea(array $params)
{
	$query = initializesql($params);
	try {
		$dbhost = $params['serverip'];
		$dbname = $params['configoption1'];
		$dbuser = $params['serverusername'];
		$dbpass = $params['serverpassword'];
		$db = new PDO('mysql:host=' . $dbhost . ';dbname=' . $dbname, $dbuser, $dbpass);
		$usage = $db->prepare($query['USERINFO']);
		$usage->bindValue(':sid', $params['serviceid']);
		$usage->execute();
		$usage = $usage->fetch();
		$nodes = $params['configoption4'];
		$results = array();
		$node = explode('|', $nodes);
		$x=0;$count=count($node)-1;
		while($x <= $count){
			$results[$x/6][$x%6] = $node[$x];
			$x++;
		}
		$user = array('uuid' => $usage['uuid'], 'u' => $usage['uplink'], 'd' => $usage['downlink'], 't' => $usage['usetime'], 'sum' => $usage['uplink'] + $usage['downlink'], 'transfer_enable' => $usage['transfer_enable'], 'created_at' => $usage['created_at'], 'updated_at' => $usage['updated_at']);
		if ($usage && $usage['enable']) {
			return array(
	'tabOverviewReplacementTemplate' => 'details.tpl',
	'templateVariables'              => array('usage' => $user, 'convert_tran' => $params, 'nodes' => $results)
	);
		}
		return array(
	'tabOverviewReplacementTemplate' => 'error.tpl',
	'templateVariables'              => array('usefulErrorHelper' => '出现了一些问题，可能您的服务还未开通，请稍后再来试试。')
	);
	}
	catch (Exception $e) {
		logModuleCall('V2rayMS', 'V2rayMS_ClientArea', $params, $e->getMessage(), $e->getTraceAsString());
		return array(
	'tabOverviewReplacementTemplate' => 'error.tpl',
	'templateVariables'              => array('usefulErrorHelper' => $e->getMessage())
	);
	}
}
function V2rayMS_AdminServicesTabFields(array $params)
{
	$query = initializesql($params);
	try {
		$dbhost = $params['serverip'];
		$dbname = $params['configoption1'];
		$dbuser = $params['serverusername'];
		$dbpass = $params['serverpassword'];
		$db = new PDO('mysql:host=' . $dbhost . ';dbname=' . $dbname, $dbuser, $dbpass);
		$userinfo = $db->prepare($query['USERINFO']);
		$userinfo->bindValue(':sid', $params['serviceid']);
		$userinfo->execute();
		$userinfo = $userinfo->fetch();
		if ($userinfo) {
			return array('UUID' => $userinfo['uuid'], '总流量' => convert_tran($userinfo['transfer_enable'], 'bytes', 'mb') . 'MB', '已用上传' => round(convert_tran($userinfo['uplink'], 'bytes', 'mb')) . 'MB', '已用下载' => round(convert_tran($userinfo['downlink'], 'bytes', 'mb')) . 'MB', '已用总量' => round(convert_tran($userinfo['downlink'] + $userinfo['uplink'], 'bytes', 'mb')) . 'MB', '最后使用' => date('Y-m-d H:i:s', $userinfo['usetime']), '上次重置' => date('Y-m-d H:i:s', $userinfo['updated_at']));
		}
	}
	catch (Exception $e) {
		logModuleCall('V2rayMS', 'V2rayMS_AdminServicesTabFields', $params, $e->getMessage(), $e->getTraceAsString());
		return $e->getTraceAsString();
	}
}
?>
