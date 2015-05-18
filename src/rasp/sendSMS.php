<?php
// This is executed whenever the raspberry receives a HTTP request of the form:
// https://[RASP_IP]/webtext/api/sendSMS.php?content=CONTENT&number=NUMBER&pass=api_secret_key

// ini_set('default_charset', 'UTF-8');
// header('Content-Type: text/html; charset=UTF-8');
// $locale='fr_FR.UTF-8';
// setlocale(LC_ALL,$locale);
// putenv('LC_ALL='.$locale);
// putenv('LANG=fr_FR.UTF-8'); 
// echo exec('locale charmap');
// echo "..";
// mb_internal_encoding('UTF-8');

$PROGRAM="/home/lutcheti/webtext/src/rasp/sendSMS.sh";
$CONTENT = $_GET['content'];
$NUMBER = $_GET['number'];
$API_SECRET_KEY = $_GET['pass'];

// echo mb_detect_encoding($CONTENT);


echo "<pre>Before</pre>";
echo "<pre>Input: content: '$CONTENT', number: '$NUMBER', api_secret_key: '$API_SECRET_KEY'.</pre>";
$output = shell_exec('sudo /home/lutcheti/webtext/src/rasp/sendSMS.sh "'.$NUMBER.'" "'.$API_SECRET_KEY.'" "'.$CONTENT.'" ');
// $output2 = shell_exec('echo "'.$NUMBER.'" "'.$API_SECRET_KEY.'" "'.$CONTENT.'" ');
echo "<pre>Output: $output.</pre>";
echo "<pre>After</pre>";
?>