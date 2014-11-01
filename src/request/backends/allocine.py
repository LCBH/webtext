import requests
import urllib
import subprocess             
import datetime

allocine_secretkey = "29d185d98c984a359e6e6f26a0474269"

def test():
    movie = "mommy"
    params = [
        ("q", movie),
        ("filter", ""),
        ("count", "16"),
        ("page" , "1"),
        ("format" , "json"),
        ("partner" , "100043982026"),
        ("sed", "".join(str(datetime.date.today()).split('-')))
        ]
    to_encrypt = allocine_secretkey + "&".join([str(k)+'='+str(val) for (k,val) in params])
    BashCommandList = "php encode.php "+to_encrypt
    process = subprocess.Popen(BashCommandList.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    params.append( ("sig", output))
    params_t = tuple(params)

    s = "http://api.allocine.fr/rest/v3/search?"+ "&".join([str(k)+'='+str(val) for (k,val) in params])
    r = requests.get(s)
    print "---"
    print r.status_code
    print "---"
    print r.headers['content-type']
    print "---"
    print r.encoding
    print "---"
    print r.text
    print "---"
    print r.json()

def search_movie(name):
    # TODO: OK if call PHP code here
    return()

def showtimes(name, where):
    # TODO: OK if call PHP code here
    return()
