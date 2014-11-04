<?php
    require_once "/home/lutcheti/webtext/src/request/backends/api-allocine-helper/api-allocine-helper.php";
    
    // Construct the object
    $allohelper = new AlloHelper;
    
    
    // Get keywords
    //    echo "Title: ";
    
    // Trim the input text.
    $search = $argv[1];
    	 //trim(substr(fgets(STDIN), 0, -1));

    //echo "ZipCode: ";
    $zip = $argv[2];
    	 //trim(substr(fgets(STDIN), 0, -1));
    
    // Parameters
    $page = 1;
    $count = 16;

    
    

    try
    {
        // Request
        $data = $allohelper->search($search, $page, $count);
        
        // No result ?
        if (!$data or count($data->movie) < 1)
            throw new ErrorException('No result for "' . $search . '"');
        
        // View number of results.
	//        echo "// " . $data->results->movie .' results for "' . $search . '":' . PHP_EOL;
        
        // For each movie result.

	$movie = $data->movie[0];

	$data2 = $allohelper->showtimesByZip($zip, $date=null,  $movieCode=$movie->code);

	if (isset($data2["feed"]) && isset($data2["feed"]["theaterShowtimes"]) && isset($data2["feed"]["theaterShowtimes"][0]["movieShowtimes"][0]["display"]))
	{
		foreach ($data2["feed"]["theaterShowtimes"] as $i => $theater)
		{
			if ($i > 4)
			{
				break;
			}
			echo "THEATER Au ". $theater["place"]["theater"]["name"].", ".$theater["place"]["theater"]["address"]."\n";
			echo $theater["movieShowtimes"][0]["display"]."\n";

		}
	}
    }   
   
    // Error
    catch (ErrorException $e)
    {
        echo "Error " . $e->getCode() . ": " . $e->getMessage() . PHP_EOL;
    }
?>
