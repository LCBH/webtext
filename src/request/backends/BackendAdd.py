from mainClass import *

class BackendAdd(Backend):
    backendName = "add"

    def answer(self, request, config):
        """ Parse a request (instance of class Request) and produce the 
        expected answer (in Unicode). """
        n1 = int(request.argsList[0])
        n2 = int(request.argsList[1])
	return("Result: " + str(n1+n2))

    def help(self):
        """ Returns a help message explaining how to use this backend 
        (in Unicode). """
	return("Type 'add; n1; n2' for adding 'n1' and 'n2'.")

    def test(self,user):
        """ Test the backend by inputting different requests and check
        the produced answer. Log everything and returns a boolean denoting
        whether the backend is broken or not (False when broken)."""
        req = Request(user, "add", [str(2), str(3)], [], "")
	answ = self.answer(req, {})
	return("Result" in answ and str(5) in answ)

bAdd = BackendAdd()
