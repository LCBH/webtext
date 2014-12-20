<?php
//    require_once "/home/lutcheti/webtext/src/request/backends/api-allocine-helper/api-allocine-helper.php";

    require_once "api-allocine-helper/api-allocine-helper.php";

    
    // Construct the object
    $allohelper = new AlloHelper;
    
    
    // Get keywords
    //    echo "Title: ";
    
    // Trim the input text.
    $search = $argv[1];
    	 //trim(substr(fgets(STDIN), 0, -1));


    $theaters = $argv[3];

    // Parameters
    $page = 1;
    $count = 16;


    try
    {
        // Request
	$data = $allohelper->search($search, $page, $count);
        
        // No result ?
        if (!$data or count($data->theater) < 1)
           throw new ErrorException('No result for "' . $search . '"');

	//        View number of results.
	//	echo "// " . $data->results->theater .' results for "' . $search . '":' . PHP_EOL;
	$th = $data->theater[0];

	$code = $th->code;
	$name = $th->name;
	

	//		$data2 = $allohelper->showtimesByZip($zip, $date=null,  $movieCode=$movie->code);

	$data2 = $allohelper->showtimesByTheaters($code);//, $zip, $date=null, $movieCode=null, $count = 10, $page = 1, $url = null);

	// if (isset($data2["feed"]))
	//    echo "feed set.\n\n";

	if (isset($data2["feed"]) && isset($data2["feed"]["theaterShowtimes"]) && isset($data2["feed"]["theaterShowtimes"][0]["movieShowtimes"]))
	{
		foreach ($data2["feed"]["theaterShowtimes"][0]["movieShowtimes"] as $i => $movie)
		{
			echo "MOVIE ".$movie["onShow"]["movie"]["title"]." (version ".$movie["version"]["$"].")\n";
			echo $movie["display"]."\n";

		}
	}
    }   
   
    // Error
    catch (ErrorException $e)
    {
        echo "Error " . $e->getCode() . ": " . $e->getMessage() . PHP_EOL;
    }
?>
