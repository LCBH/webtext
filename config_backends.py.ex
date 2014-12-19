CONF = {
    'config_database' : {
        'path' : 'data/database/',
        'file' : 'name.db',
        },
    'config_backends' :  {
        'jcdecaux' : {
            'API_key' : 'yourJcDecauxKey',
            }
        },  
    'config_api' : {
        'api_secret_key' : "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        },		 
    'users' : [
        {
            'login' : "luccaH",
            'name' : "Lucca Hirschi",
            'number' : "06XXXXXXXX",
            'email' : "XXXX@XXXX.XXX",
            'sendSMS' : {
                'method' : "FREE_API",
                'login' : "XXXXXXXx",
                'password' : "XXXXXXXXXXXXXXXX",
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

