<?php
// This is executed whenever the request server receives a HTTP request of the form:
// https://www.choum.net/webtext/api/sms.php?pass=API_SECRET_KEYY&numero=NUMERO&content=CONTENT

$PASS = $_GET['pass'];
$NUMERO = $_GET['numero'];
$CONTENT = $_GET['content'];

echo 'sudo screen -S parseAndSendOnRequest -d -m  python $PROGRAM \"\${NUMERO}\" \"\${CONTENT}\" \"false\" \"\${PASS}\" &';
?>'