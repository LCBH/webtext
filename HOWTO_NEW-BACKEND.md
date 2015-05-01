HOWTO addig a new backend (service)
===================================

The main working folder is src/request/.

## Basics
In a nutshell, a service should provide a backend with a main function
'answer' that takes a request and produce an answer.


### Requests
A request is an object of the following class (defined in 'src/request/request.py'):
````python
class Request:
    """Based class for requests."""
    def __init__(self, user, backendName, argsList, optionsList, requestCore):
        self.user = user                # dictionnary describing user
        self.backend = backendName      # UTF8 string
        self.argsList = argsList        # List of UTF8 strings
        self.optionsList = optionsList  # List of UTF8 strings
        self.raw = requestCore          # UTF8 string

    def __str__(self):  [...]
````
The label 'user' contains a dictionnary describing the user.
See './config_backends.py.ex' to see an example of such a dictionnary.
The most important part is the label 'argsList' containing the list of
arguments of the request.
For instance, the text 'yelp; arg1; arg2' produces the request whose
'backend' is 'yelp' and 'argsList' is '["arg1"; "arg2"].


### Backends
A backend should be defined as a sub-class of the main class 'backend'
(defined in ./src/request.backends/mainClass.py). Only 3 methods should
be (re)defined: 'answer', 'help' and 'test'.
The (main) method 'answer' takes a request and produce an answer.
The method 'help' will is called returned when one requests 'help; [BackendName]'.
The method 'test' should test all kinds of requests on the backend.

For instance, the backend providing a service 'addition' can be defined like this
(see the full file in './src/request/backends/BackendAdd.py'):
````python
class BackendAdd(Backend):
    backendName = "add"

    def answer(self, request, config):
        """ Parse a request (instance of class Request) and produce the 
        expected answer (in Unicode). """
	return("Result: " + str(request.argsList[0] + request.argsList[1]))

    def help(self):
        """ Returns a help message explaining how to use this backend 
        (in Unicode). """
	return("Type 'add; n1; n2' for adding 'n1' and 'n2'.")

    def test(self,user):
        """ Test the backend by inputting different requests and check
        the produced answer. Log everything and returns a boolean denoting
        whether the backend is broken or not (False when broken)."""
        req = Request(user, "add", [str(2) + str(3)], [], "")
	answ = self.answer(req, {})
	return("Result" in answ and str(5) in answ)
````


## Files to write/modify:
- A new file containing the sub-class of Backend must be created in backends/
(see the file './src/request/backends/BackendAdd.py' for an example).
Use the following nomenclature 'Backend[BackendName].py' (e.g., 'BackendYelp.py').
This file must also create an object of this sub-class.
Use the following nomenclature: 'b[BackendName] (e.g., 'bYelp = BackendYelp()');
- this module must be imported in backends/main.py by adding the following line:
````python
from Backend[BackendName] import b[BackendName]
````
(e.g., from BackendYelp import bYelp).


## Testing
Type 'python test.py' to launch all tests of all backends (incuding
the new one you just added). You can also type 'python test.py i' to launch a prompt
that allows you to interact with webtext (you can type a request and then the answer is displayed).


## Advanced usages

### Database
If needed, you can use the database of webtext by adding a new table.
See 'database/db.py' and 'database/test.py' for more details.
