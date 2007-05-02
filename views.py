"""Uses SimpleXMLRPCServer's SimpleXMLRPCDispatcher to serve XML-RPC requests"""
from django.core.exceptions import ImproperlyConfigured
from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
from xmlrpclib import Fault
from django.http import HttpResponse, HttpResponseServerError
from django.conf import settings
from django.shortcuts import render_to_response
import sys

# Declare xmlrpcdispatcher correctly depending on our python version
if sys.version_info[:3] >= (2,5,):
    xmlrpcdispatcher = SimpleXMLRPCDispatcher(allow_none=False, encoding=None)
else:
    xmlrpcdispatcher = SimpleXMLRPCDispatcher()

def test_xmlrpc(text):
    """
    Simply returns the args passed to it as a string
    """
    return "Here's a response! %s" % str(locals())

def handle_xmlrpc(request):
    """
    Handles XML-RPC requests. All XML-RPC calls should be forwarded here

    request
        The HttpRequest object that carries the XML-RPC call. If this is a
        GET request, nothing will happen (we only accept POST requests)
    """
    response = HttpResponse()
    if request.method == "POST":
        try:
            response.write(
                xmlrpcdispatcher._marshaled_dispatch(request.raw_post_data))
            return response
        except Exception, e:
            return HttpResponseServerError()
    else:
        return render_to_response(settings.XMLRPC_GET_TEMPLATE)

# Load up any methods that have been registered with the server in settings
for path, name in settings.XMLRPC_METHODS:
    # if "path" is actually a function, just add it without fuss
    if callable(path):
        xmlrpcdispatcher.register_function(path, name)
        continue

    # Otherwise we try and find something that we can call
    i = path.rfind('.')
    module, attr = path[:i], path[i+1:]

    try:
        mod = __import__(module, globals(), locals(), [attr])
    except ImportError, e:
        raise ImproperlyConfigured, "Error registering XML-RPC method: " \
              + "module %s can't be imported" % module

    try:
        func = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured, 'Error registering XML-RPC method: ' \
              + 'module %s doesn\'t define a method "%s"' % (module, attr)

    if not callable(func):
        raise ImproperlyConfigured, 'Error registering XML-RPC method: ' \
              + '"%s" is not callable in module %s' % (attr, module)

    xmlrpcdispatcher.register_function(func, name)
