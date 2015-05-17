# -- coding: utf-8 --
CONF = {
    'config_database' : {
        'path' : 'data/database/',
        'file' : 'name.db',
        },
    'config_backends' :  {
        'jcdecaux' : {
            'API_key' : 'yourJcDecauxKey',
            },
	'navitia' : {
	    'API_key' : 'yourNavitiaKey',
            },
        'yelp' : {
            'consumer_key' : 'XXXX',
            'consumer_secret' : 'XXX',
            'token' : 'XXX',
            'token_secret' : 'XXX',
            },
        },  
    'config_api' : {
        'api_secret_key' : "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        'ip_raspberry' : 'XXXXXXXXXXXX',
        },		 
    'users' : [
        {
            'login' : "luccaH",
            'name' : "Lucca Hirschi",
            'number' : "06XXXXXXXX",
            'email' : "XXXX@XXXX.XXX",
            'sendSMS' : {
                'method' : "RASP",    # either by using the rasp's SIM (RASP) or free's API (FREE_API)
                },
            'shortcuts' :  [      # list of (received request, sequence of requests to perform)"
                ("velo", ["velo marx dormoy", "velo riquet"]),
                ("retour", ["ratp bagneux", "velo"])
                ]
            },
        {
            'login' : 'vincentCA',
            'name' : "Vincent Cohen-Addad",
            'number' : "06XXXXXXXX",
            'email' : "XXXXX@XXXX.XX",
            'sendSMS' : {
                'method' : "FREE_API",
                'login' : "XXXXXXXXXXXX",
                'password' : "XXXXXXXXXXXXXXX",
                }
            }
        ]
    }

