<?php
	$sig = urlencode(base64_encode(sha1($argv[1], true)));
	echo $sig;
?>