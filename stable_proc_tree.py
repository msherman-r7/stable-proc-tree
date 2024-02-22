from ctypes import *
import sys

ERROR_SUCCESS = 0
ERROR_ALREADY_EXISTS = 183

WAIT_OBJECT_0 = 0
WAIT_TIMEOUT = 0x102
WAIT_FAILED = -1

EVENT_MODIFY_STATE = 0x0002
SYNCHRONIZE = 0x00100000

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

def errcheckOpenEvent(result, func, args):
    le = get_last_error()
    if result == INVALID_HANDLE_VALUE:
        raise WinError(le)
    return result

def errCheckWait(result, func, args):
    if result == WAIT_FAILED:
        raise WinError(get_last_error())
    return result

class Proc:
    def __init__(self, info):
        self.info = info

    def wait_to_exit(self):
        return WAIT_TIMEOUT

    def terminate(self):
        return True, ERROR_SUCCESS

def create_event(name):
    createEventW = _kernel32_dll.CreateEventW
    createEventW.restype = c_void_p
    createEventW.errcheck = errcheckCreateEvent

    event_name = create_unicode_buffer("stable_proc_event_" + name)

    handle = createEventW(None, 1, 0, event_name)
    return handle

def open_event(name):
    openEventW = _kernel32_dll.OpenEventW
    openEventW.restype  = c_void_p
    openEventW.errcheck = errcheckOpenEvent

    event_name = create_unicode_buffer("stable_proc_event_" + name)

    handle = openEventW(EVENT_MODIFY_STATE | SYNCHRONIZE, 0, event_name)
    return handle 

def wait_event(event_handle, timeout_ms):
    waitForSingleObject = _kernel32_dll.WaitForSingleObject
    waitForSingleObject.restype = c_uint
    waitForSingleObject.errcheck = errCheckWait

    result = waitForSingleObject(event_handle, timeout_ms)
    return result 

def set_event(event_handle):
    setEvent = _kernel32_dll.SetEvent 
    setEvent.restype = c_uint
    setEvent.errcheck = errcheck
    
    setEvent(event_handle)

def create_proc(depth):
    createProcessW = _kernel32_dll.CreateProcessW
    createProcessW.restype = c_uint
    createProcessW.errcheck = errcheck 

    cmd_line = create_unicode_buffer(sys.executable + " stable_proc_tree.py " + depth) 
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
    print(sys.argv, len(sys.argv))
    ready_event = open_event(sys.argv[1])

    depth_as_int = int(sys.argv[1])
    if depth_as_int > 1:
        depth_as_int = depth_as_int - 1
        depth_as_str = str(depth_as_int)
        child_ready_event = create_event(depth_as_str) 
        create_proc(depth_as_str)
        wait_result = wait_event(child_ready_event, 1000 * 5)
        if wait_result == WAIT_OBJECT_0:
            set_event(ready_event) 
        else:
            print("Timed out while waiting for child at depth " + depth_as_str)
    else:
        set_event(ready_event) 
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

