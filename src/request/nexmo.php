
<?php
echo "<pre>Before</pre>";
// work with get or post
$request = array_merge($_GET, $_POST);

// check that request is inbound message
if(!isset($request['to']) OR !isset($request['msisdn']) OR !isset($request['text'])){
  error_log('not inbound message');
  return;
}
echo "<pre>Sanity Check ok</pre>";

$PROGRAM="/home/lutcheti/webtext/src/request/handleSMS.py";
$NUMERO = escapeshellarg($request['msisdn']);
$CONTENT = escapeshellarg($request['text']);
$PASS = escapeshellarg("no");
$isTesting = "false";
$isLocal = "false";

echo "<pre>Input: numero: $NUMERO, content: $CONTENT; pass: $PASS.</pre>";
// POUR QUITTER LE MODE TESTING et vraiment envoyer les réponses aux requêtes par SMS, mettre le premier boolean à false
$output2 = shell_exec('sudo python /home/lutcheti/webtext/src/request/handleSMS.py ' . ' ' . $NUMERO . ' ' . $CONTENT . ' ' . $isTesting . ' ' . $isLocal . ' ' . $PASS);
echo "<pre>Output: $output</pre>";
$output2 = shell_exec('sudo -u lutcheti whoami');
$output3 = shell_exec('whoami');
echo "<pre>Output2:  $output2 / $output3</pre>";
echo "<pre>After</pre>";
?>
