#import requests
import urllib
import subprocess             
import datetime
import copy
from datetime import date
#from datetime import date
import urllib2
import hashlib, base64
import simplejson

allocine_secretkey = "29d185d98c984a359e6e6f26a0474269"
params = [
    ("format" , "json"),
#    ("partner" , "aXBob25lLXYy"),
    ("partner" , "100043982026")
    #    ("partner", "QUNXZWItQWxsb0Npbuk"),
]    

def digest_movie(rep):
    s = "Resultats:\n"
    
    print "Digest... "
    for c in rep["movie"]:
        s+=c['title']+", sorti le "+c["release"]["releaseDate"]+", realise par "+c['castingShort']['directors']+"\n"
    print "--------"
    print s
    print "--------"

def digest_times(rep):
    s = "Resultats:\n"
    
    print "Digest... "
    for c in rep:
        print "key %s ==> %s" %(c,rep[c])
    print "--------"
    print s
    print "--------"

    
def search_movie(movie):
    p = copy.deepcopy(params)
    p.insert(0,("count", "16"))
    p.insert(0,("page" , "1"))
    p.insert(0,("filter", "movie"))
    p.insert(0,("q", movie))
    p.append(("sed", "".join(str(datetime.date.today()).split('-'))))
    to_encrypt = allocine_secretkey + "&".join([str(k)+'='+str(val) for (k,val) in p])

    BashCommandList = "php encode.php "+to_encrypt
    #BashCommandList = "php encode.php "+to_encrypt
    process = subprocess.Popen(BashCommandList.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]

    sed = "".join(str(datetime.date.today()).split('-'))
    #print sed
    sha1 = hashlib.sha1(allocine_secretkey+urllib.urlencode(p)+'&sed='+sed).digest()
    #print sha1
    b64 = base64.b64encode(sha1)
    #print b64
    sig = urllib2.quote(b64)

    print "sig:", sig

    p.append( ("sig", sig))

    params_t = tuple(p)
    
    
    s = "http://api.allocine.fr/rest/v3/search?"+urllib.urlencode(params_t, True)

    r = urllib2.Request(s)
    r.add_header('User-agent', 'AlloCine/2.9.5 CFNetwork/548.1.4 Darwin/11.0.0')
    #r.add_header('User-agent', "Mozilla/5.0 (Linux; U; Android $v; fr-fr; LG-P5$b Build/FRG83) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1")

    response = simplejson.load(urllib2.urlopen(r, timeout = 10))
    if not "feed" in response or response["feed"] == None:
        return "Error"
    else:
        digest_movie(response["feed"])
        return "Done."


        

def showtimes(movie, zip_code = None, theater = None):
    # TODO: OK if call PHP code here
    p = copy.deepcopy(params)
    # p.insert(0,("filter", ""))
    # p.insert(0,("q", movie))
    if zip_code != None:
        p.append(("zip", zip_code))
    else:
        p.append(("theaters", theaters))       
    to_encrypt = allocine_secretkey + "&".join([str(k)+'='+str(val) for (k,val) in p])
    #    BashCommandList = "php backends/encode.php "+to_encryp

    BashCommandList = "php encode.php "+to_encrypt
    process = subprocess.Popen(BashCommandList.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]

    sed = "".join(str(datetime.date.today()).split('-'))
    #print sed
    sha1 = hashlib.sha1(allocine_secretkey+urllib.urlencode(p)+'&sed='+sed).digest()
    #print sha1
    b64 = base64.b64encode(sha1)
    #print b64
    sig = urllib2.quote(b64)
    
    p.append( ("sig", sig))
    params_t = tuple(p)

    s = "http://api.allocine.fr/rest/v3/showtimelist?"+urllib.urlencode(params_t, True)
    print s
    r = urllib2.Request(s)
    r.add_header('User-agent', 'AlloCine/2.9.5 CFNetwork/548.1.4 Darwin/11.0.0')

    #r.add_header('User-agent',                 "Mozilla/5.0 (Linux; U; Android $v; fr-fr; LG-P5$b Build/FRG83) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1")

    response = simplejson.load(urllib2.urlopen(r, timeout = 20))
    if not "feed" in response or response["feed"] == None:
        return "Error"
    else:
        digest_times(response["feed"])
        return "Done."


def showtimes2():
    p = [
        ("q", "mommy"),
        ("filter", ""),
        ("count", "10"),
        ("page", "1"),
        ("format" , "json"),
        ("partner" , "100043982026"),
        ("zip", "75013"),
        ("movie", "223002")
    ]

    sed = "".join(str(datetime.date.today()).split('-'))
    p.append(("sed",sed))
    to_encrypt = allocine_secretkey + "&".join([str(k)+'='+str(val) for (k,val) in p])

    BashCommandList = "php backends/allocine_encode.php "+to_encrypt
    process = subprocess.Popen(BashCommandList.split(), stdout=subprocess.PIPE)
    sig = process.communicate()[0]
    sha1 = hashlib.sha1(allocine_secretkey+urllib.urlencode(p)+'&sed='+sed).digest()
    #print sha1
    b64 = base64.b64encode(sha1)
    #print b64
    sig2 = urllib2.quote(b64)
    print "sig2", sig2
    #p.append( ("sig", "RktsLjLzL5cgYdg55hzslRkg6vc%3D"))
    p.append( ("sig", sig2))
    params_t = tuple(p)

    s = "http://api.allocine.fr/rest/v3/showtimelist?"+urllib.urlencode(params_t, True)
    r = urllib2.Request(s)
    r.add_header('User-agent', 'AlloCine/2.9.5 CFNetwork/548.1.4 Darwin/11.0.0')

    #r.add_header('User-agent',                 "Mozilla/5.0 (Linux; U; Android $v; fr-fr; LG-P5$b Build/FRG83) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1")
    print s
    response = simplejson.load(urllib2.urlopen(r, timeout = 20))
    if not "feed" in response or response["feed"] == None:
        return "Error"
    else:
        digest_times(response["feed"])
        return "Done."
    


#print search_movie("lotr")
#print showtimes("Mommy", zip_code="75013")
print showtimes2()
