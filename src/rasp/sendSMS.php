<?php
// This is executed whenever the raspberry receives a HTTP request of the form:
// https://[RASP_IP]/webtext/api/sendSMS.php?content=CONTENT&number=NUMBER

$PROGRAM="/home/lutcheti/webtext/src/rasp/sendSMS.sh";
$CONTENT = $_GET['content'];
$NUMBER = $_GET['number'];

echo "<pre>Before</pre>";
echo "<pre>Input: content: $CONTENT, number: $NUMBER.</pre>";
$output = shell_exec('sudo /home/lutcheti/webtext/src/rasp/sendSMS.sh "'.$CONTENT.'" "'.$NUMBER.'" ');
echo "<pre>Output: (no output but see the logs) $output</pre>";
echo "<pre>After</pre>";
?>