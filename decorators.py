"""
Offers decorators to make the use of django_xmlrpc a great deal simpler

Credit must go to Brendan W. McAdams <brendan.mcadams@thewintergrp.com>, who
posted the original SimpleXMLRPCDispatcher to the Django wiki:
http://code.djangoproject.com/wiki/XML-RPC

New BSD License
===============
Copyright (c) 2007, Graham Binns

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.
    * Neither the name of the <ORGANIZATION> nor the names of its contributors
      may be used to endorse or promote products derived from this software
      without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
from xmlrpclib import Fault
from django.contrib.auth import authenticate
from django.utils.translation import gettext as _

def xmlrpc_func(returns='string', args=[], name=''):
    """
    A decorator for XML-RPC-exposed methods. Adds a signature to an XML-RPC
    function.

    returns
        The return type of the function. This can either be a string
        description (e.g. 'string') or a type (e.g. str, bool) etc.

    args
        A list of the types of the arguments that the function accepts. These
        can be strings or types or a mixture of the two e.g.
        [str, bool, 'string']

    name
        The XML-RPC name to give the function (e.g. metaweblog.getPost) as a
        string. If this is not specified or otherwise left empty, the method
        will not be registered with the dispatcher. This allows us to specify
        signatures for methods that are registered with the dispatcher via
        settings.XMLRPC_METHODS
    """
    def _xmlrpc_func(func):
        # Add the function to the dispatcher
        if name:
            # We do this import here to avoid circular references and what have
            # you
            from views import xmlrpcdispatcher
            xmlrpcdispatcher.register_function(func, name)

        # Add a signature to the function
        func._xmlrpc_signature = {
            'returns': returns,
            'args': args
        }
        return func

    return _xmlrpc_func

#fixme: Any standardization?
AuthenticationFailedCode = 81
PermissionDeniedCode = 82

class AuthenticationFailedException(Fault):
    def __init__(self):
        Fault.__init__(self, AuthenticationFailedCode,
            _('Username and/or password is incorrect'))

class PermissionDeniedException(Fault):
    def __init__(self):
        Fault.__init__(self, PermissionDeniedCode, _('Permission denied'))

# Don't use this decorator when your service is going to be
# available in an unencrpted/untrusted network.
# Configure HTTPS transport for your web server.
def permission_required(perm=None):
    "Decorator for authentication. (fixme:docstring)"
    def _dec(func):
        def __authenticated_call(username, password, *args):
            try:
                user = authenticate(username=username, password=password)
                if not user:
                    raise AuthenticationFailedException
                if perm and not user.has_perm(perm):
                    raise PermissionDeniedException
            except AuthenticationFailedException:
#                log.error("Authentication Failed for username '%s'" % username)
                raise
            except PermissionDeniedException:
#                log.error(("Permission Denied. Username: '%s', " + \
#                    "Required permission: %s") % (username, perm))
                raise
            except:
#                log.error(traceback.format_exc())
                raise AuthenticationFailedException
            return func(user, *args)

        #fixme: update _xmlrpc_signature
        if func.__doc__:
            __authenticated_call.__doc__ = func.__doc__ + \
            "\nNote: Authentication is required."""
            if perm:
                __authenticated_call.__doc__ += ' this function requires "%s" permission.' % perm

        return __authenticated_call

    return _dec
