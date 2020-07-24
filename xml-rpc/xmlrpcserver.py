import html
from functools import partial
import http.server
import socketserver
import sys
import os
import re
import pydoc
import xml-rpcclient

class XMLRPCDispatcher:

    def __init__(self, encoding=None):
        self.funcs = {}
        self.instance = None
        self.encoding = encoding or 'utf-8'
    
    def register_function(self, function=None, name=None):
        """缓存用于使用rpc服务的函数，函数的调用可以根据对应的函数名或者特有的编号"""
        if function is None:
            return partial(self.register_function, name=name)

        if name is None:
            name = function.__name__
            
        self.funcs[name] = function

        return function

    def _marshaled_dispatch(self, data, dispatch_method = None, path = None):
        """Dispatches an XML-RPC method from marshalled (XML) data.
        XML-RPC methods are dispatched from the marshalled (XML) data
        using the _dispatch method and the result is returned as
        marshalled data. For backwards compatibility, a dispatch
        function can be provided as an argument (see comment in
        SimpleXMLRPCRequestHandler.do_POST) but overriding the
        existing method through subclassing is the preferred means
        of changing method dispatch behavior.
        """

        try:
            params, method = loads(data, use_builtin_types=self.use_builtin_types)

            # generate response
            if dispatch_method is not None:
                response = dispatch_method(method, params)
            else:
                response = self._dispatch(method, params)
            # wrap response in a singleton tuple
            response = (response,)
            response = dumps(response, methodresponse=1,
                             allow_none=self.allow_none, encoding=self.encoding)
        except Fault as fault:
            response = dumps(fault, allow_none=self.allow_none,
                             encoding=self.encoding)
        except:
            # report exception back to server
            exc_type, exc_value, exc_tb = sys.exc_info()
            try:
                response = dumps(
                    Fault(1, "%s:%s" % (exc_type, exc_value)),
                    encoding=self.encoding, allow_none=self.allow_none,
                    )
            finally:
                # Break reference cycle
                exc_type = exc_value = exc_tb = None

        return response.encode(self.encoding, 'xmlcharrefreplace')

    def system_listMethods(self):
        """system.listMethods() => ['add', 'subtract', 'multiple']
        Returns a list of the methods supported by the server."""

        methods = set(self.funcs.keys())
        if self.instance is not None:
            # Instance can implement _listMethod to return a list of
            # methods
            if hasattr(self.instance, '_listMethods'):
                methods |= set(self.instance._listMethods())
            # if the instance has a _dispatch method then we
            # don't have enough information to provide a list
            # of methods
            elif not hasattr(self.instance, '_dispatch'):
                methods |= set(list_public_methods(self.instance))
        return sorted(methods)
    
    def _dispatch(self, method, params):
        """Dispatches the XML-RPC method.
        XML-RPC calls are forwarded to a registered function that
        matches the called XML-RPC method name. If no such function
        exists then the call is forwarded to the registered instance,
        if available.
        If the registered instance has a _dispatch method then that
        method will be called with the name of the XML-RPC method and
        its parameters as a tuple
        e.g. instance._dispatch('add',(2,3))
        If the registered instance does not have a _dispatch method
        then the instance will be searched to find a matching method
        and, if found, will be called.
        Methods beginning with an '_' are considered private and will
        not be called.
        """

        try:
            # call the matching registered function
            func = self.funcs[method]
        except KeyError:
            pass
        else:
            if func is not None:
                return func(*params)
            raise Exception('method "%s" is not supported' % method)

        if self.instance is not None:
            if hasattr(self.instance, '_dispatch'):
                # call the `_dispatch` method on the instance
                return self.instance._dispatch(method, params)

            # call the instance's method directly
            try:
                func = resolve_dotted_attribute(
                    self.instance,
                    method,
                    self.allow_dotted_names
                )
            except AttributeError:
                pass
            else:
                if func is not None:
                    return func(*params)

        raise Exception('method "%s" is not supported' % method)

class SimpleXMLRPCServer(socketserver.TCPServer,
                         SimpleXMLRPCDispatcher):
    """Simple XML-RPC server.
    Simple XML-RPC server that allows functions and a single instance
    to be installed to handle requests. The default implementation
    attempts to dispatch XML-RPC calls to the functions or instance
    installed in the server. Override the _dispatch method inherited
    from SimpleXMLRPCDispatcher to change this behavior.
    """

    allow_reuse_address = True

    # Warning: this is for debugging purposes only! Never set this to True in
    # production code, as will be sending out sensitive information (exception
    # and stack trace details) when exceptions are raised inside
    # SimpleXMLRPCRequestHandler.do_POST
    _send_traceback_header = False

    def __init__(self, addr, requestHandler=SimpleXMLRPCRequestHandler,
                 logRequests=True, allow_none=False, encoding=None,
                 bind_and_activate=True, use_builtin_types=False):
        self.logRequests = logRequests

        SimpleXMLRPCDispatcher.__init__(self, allow_none, encoding, use_builtin_types)
        socketserver.TCPServer.__init__(self, addr, requestHandler, bind_and_activate)