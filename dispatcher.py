"""
Offers a simple XML-RPC dispatcher for django_xmlrpc

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
from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
from inspect import getargspec

class DjangoXMLRPCDispatcher(SimpleXMLRPCDispatcher):
    """
    A simple XML-RPC dispatcher for Django.

    Subclassess SimpleXMLRPCServer.SimpleXMLRPCDispatcher for the purpose of
    overriding certain built-in methods (it's nicer than monkey-patching them,
    that's for sure).
    """

    def system_methodSignature(self, method):
        """
        Returns the signature details for a specified method

        method
            The name of the XML-RPC method to get the details for
        """
        # See if we can find the method in our funcs dict
        func = self.funcs[method] # TODO: Handle this better

        try:
            sig = func._xmlrpc_signature
        except:
            sig = {'return_type': 'string', 'arg_list': [],}

            # See if the method has any _xmlrpc_* attributes
            try:
                sig['return_type'] = func._xmlrpc_return_type
            except AttributeError:
                pass

            # Try to get the arg list from documentation. Otherwise, use
            # getargspec
            # to take a punt
            try:
                sig['arg_list'] = func._xmlrpc_arg_list
            except AttributeError:
                sig['arg_list'] = ['string' for arg in getargspec(func)[0]]

        return [sig['return_type'],] + sig['arg_list']
