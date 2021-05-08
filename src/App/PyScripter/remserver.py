import sys
if len(sys.argv) > 2:
    sys.path.insert(0, sys.argv[2])

from rpyc.utils.server import Server
from rpyc.utils.classic import DEFAULT_SERVER_PORT
from rpyc.core import SlaveService
from rpyc.core.stream import NamedPipeStream
from rpyc.utils.factory import connect_stream
import threading

__traceable__ = 0

class SimpleServer(Server):
    def _accept_method(self, sock):
        try:
            self._serve_client(sock, None)
        finally:
            self.close()

class ModSlaveService(SlaveService):
    __slots__ = []

    def on_connect(self, conn):
        import imp
        from rpyc.core.service import ModuleNamespace

        sys.modules["__oldmain__"] = sys.modules["__main__"]
        sys.modules["__main__"] = imp.new_module("__main__")
        self.namespace = sys.modules["__main__"].__dict__

        conn._config.update(dict(
            allow_all_attrs = True,
            allow_pickle = True,
            allow_getattr = True,
            allow_setattr = True,
            allow_delattr = True,
            allow_exposed_attrs = False,
            import_custom_exceptions = True,
            instantiate_custom_exceptions = True,
            instantiate_oldstyle_exceptions = True,
        ))
        # shortcuts
        conn.modules = ModuleNamespace(conn.root.getmodule)
        conn.eval = conn.root.eval
        conn.execute = conn.root.execute
        conn.namespace = conn.root.namespace
        if sys.version_info[0] > 2:
            conn.builtin = conn.modules.builtins
        else:
            conn.builtin = conn.modules.__builtin__

##def printcrt(s):
##    import msvcrt
##    for c in s:
##        msvcrt.putwch(c)

def main():
    import warnings
    warnings.simplefilter("ignore", DeprecationWarning)

    try:
        port = int(sys.argv[1])
    except:
        port = DEFAULT_SERVER_PORT

    conn = None
    if port > 19000:
        # Named server
        try:
            __import__("win32file")
            np_server = NamedPipeStream.create_server(str(port))
            conn = connect_stream(np_server, ModSlaveService)
            try:
                conn.serve_all()
            except Exception:
                pass
            finally:
                if (conn is not None) and not conn.closed:
                    conn.close()
                exit()
        except SystemExit:
            raise
        except:
            conn = None

    if conn is None:
        t = SimpleServer(ModSlaveService, port = port, auto_register = False)
        t.start()

if __name__ == "__main__":
    main()
