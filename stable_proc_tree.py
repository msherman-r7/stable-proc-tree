from ctypes import *
import sys

ERROR_SUCCESS = 0
ERROR_ALREADY_EXISTS = 183
WAIT_OBJECT_0 = 0
WAIT_TIMEOUT = 0x102

INVALID_HANDLE_VALUE = -1

class STARTUPINFOW(Structure):
    _fields_ = [("cb", c_uint),
                ("lpReserved", c_wchar_p),
                ("lpDesktop", c_wchar_p),
                ("lpTitle", c_wchar_p),
                ("dwX", c_uint),
                ("dwY", c_uint),
                ("dwXSize", c_uint),
                ("dwYSize", c_uint),
                ("dwXCountChars", c_uint),
                ("dwYCountChars", c_uint),
                ("dwFillAttribute", c_uint),
                ("dwFlags", c_uint),
                ("wShowWindow", c_ushort),
                ("cbReserved2", c_ushort),
                ("lpReserved2",c_void_p),
                ("hStdInput",c_void_p),
                ("hStdOutput",c_void_p),
                ("hStdError",c_void_p)] 

class PROCESS_INFORMATION(Structure):
    _fields_ = [("hProcess", c_void_p),
                ("hThread", c_void_p),
                ("dwProcessId", c_uint),
                ("dwThreadId", c_uint)]

_kernel32_dll = WinDLL("kernel32", use_last_error=True)

def errcheck(result, func, args):
    if not result:
        raise WinError(get_last_error())
    return result

def errcheckCreateEvent(result, func, args):
    le = get_last_error()
    if result == INVALID_HANDLE_VALUE:
        raise WinError(le)
    if le == ERROR_ALREADY_EXISTS:
        raise WinError(le)
    return result

class Proc:
    def __init__(self, info):
        self.info = info

    def wait_to_exit(self):
        return WAIT_TIMEOUT

    def terminate(self):
        return True, ERROR_SUCCESS

def create_event(name="d1"):
    createEventW = _kernel32_dll.CreateEventW
    createEventW.restype = c_void_p
    createEventW.errcheck = errcheckCreateEvent

    event_name = create_unicode_buffer("stable_proc_event_" + name)

    handle = createEventW(None, 1, 0, event_name)
    return handle

def create_proc(depth=1):
    createProcessW = _kernel32_dll.CreateProcessW
    createProcessW.restype = c_uint
    createProcessW.errcheck = errcheck 

    cmd_line = create_unicode_buffer(sys.executable + " --version") 
    #cmd_line = create_unicode_buffer("fooooo.exe" + " --version") 

    si = STARTUPINFOW(sizeof(STARTUPINFOW), None, None, None,
                        0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0,
                        None, None, None, None)

    pi = PROCESS_INFORMATION(None, None, 0, 0)

    result = createProcessW(None, cmd_line, None, None, 0, 0, None, None, byref(si), byref(pi))
    proc = Proc(info=pi)
             
    return proc

def main():
    pass

if __name__ == '__main__':
    sys.exit(main())

