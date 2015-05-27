<?php
// This is executed whenever the request server receives a HTTP request of the form:
// https://www.choum.net/webtext/api/sms.php?pass=API_SECRET_KEYY&numero=NUMERO&content=CONTENT&isTesting=BOOL

$PROGRAM="/home/lutcheti/webtext/src/request/handleSMS.py";
$PASS = escapeshellarg($_GET['pass']);
$NUMERO = escapeshellarg($_GET['numero']);
$CONTENT = escapeshellarg($_GET['content']);
$isTesting = escapeshellarg($_GET['isTesting']);
$isLocal = "false";

echo "<pre>Before</pre>";
echo "<pre>Input: numero: $NUMERO, content: $CONTENT; pass: $PASS.</pre>";
// POUR QUITTER LE MODE TESTING et vraiment envoyer les réponses aux requêtes par SMS, mettre le premier boolean à false
$output = shell_exec('sudo python /home/lutcheti/webtext/src/request/handleSMS.py ' . ' ' . $NUMERO . ' ' . $CONTENT . ' ' . $isTesting . ' ' . $isLocal . ' ' . $PASS);
echo "<pre>Output: (no output but see the logs) $output</pre>";
echo "<pre>After</pre>";
?>

