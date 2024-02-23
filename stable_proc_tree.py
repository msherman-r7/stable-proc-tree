from ctypes import *
import sys

ERROR_SUCCESS = 0
ERROR_ALREADY_EXISTS = 183

WAIT_OBJECT_0 = 0
WAIT_TIMEOUT = 0x102
WAIT_FAILED = -1
INFINITE = -1

EVENT_MODIFY_STATE = 0x0002
SYNCHRONIZE = 0x00100000

INVALID_HANDLE_VALUE = c_void_p(-1)

PAGE_READONLY = 0x02
PAGE_READWRITE = 0x04
SEC_COMMIT = 0x08000000

FILE_MAP_WRITE = 0x0002
FILE_MAP_READ = 0x0004

READY_EVENT = "stable_ready_event_"
RESUME_EVENT = "stable_resume_event_"
SHARED_MEM = "stable_shared_mem_"

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

def errcheckNoDocumentedFailure(result, func, args):
    return result 

def errcheck(result, func, args):
    if not result:
        raise WinError(get_last_error())
    return result

def errcheckCreateSharedMem(result, func, args):
    le = get_last_error()
    if result == None:
        raise WinError(le)
    if le == ERROR_ALREADY_EXISTS:
        raise WinError(le)
    return result

def errcheckOpenSharedMem(result, func, args):
    le = get_last_error()
    if result == None:
        raise WinError(le)
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

def create_shared_memory(access, prefix, depth):
    createFileMappingW = _kernel32_dll.CreateFileMappingW
    createFileMappingW.restype = c_void_p 
    createFileMappingW.errcheck =  errcheckCreateSharedMem

    shared_mem_name = create_unicode_buffer(prefix + depth)

    handle = createFileMappingW(INVALID_HANDLE_VALUE, None, access, 0, 8, shared_mem_name)
    return handle

def open_shared_memory(access, prefix, depth):
    openFileMappingW = _kernel32_dll.OpenFileMappingW
    openFileMappingW.restype = c_void_p
    openFileMappingW.errcheck = errcheckOpenSharedMem

    shared_mem_name = create_unicode_buffer(prefix + depth)

    handle = openFileMappingW(access, 0, shared_mem_name)
    return handle 

def map_view_of_shared_memory(shared_mem, access):
    mapViewOfFile = _kernel32_dll.MapViewOfFile
    mapViewOfFile.restype = c_void_p
    mapViewOfFile.errcheck = errcheckOpenSharedMem

    ptr = mapViewOfFile(shared_mem, access, 0, 0, 8) 
    return ptr

def unmap_view_of_shared_memory(ptr):
    unmapViewOfFile = _kernel32_dll.UnmapViewOfFile
    unmapViewOfFile.restype = c_uint 
    unmapViewOfFile.errcheck = errcheck 

    result = unmapViewOfFile(ptr)
    return result 

def create_event(prefix, depth):
    createEventW = _kernel32_dll.CreateEventW
    createEventW.restype = c_void_p
    createEventW.errcheck = errcheckCreateEvent

    event_name = create_unicode_buffer(prefix + depth)

    handle = createEventW(None, 1, 0, event_name)
    return handle

def open_event(prefix, depth):
    openEventW = _kernel32_dll.OpenEventW
    openEventW.restype  = c_void_p
    openEventW.errcheck = errcheckOpenEvent

    event_name = create_unicode_buffer(prefix + depth)

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

def close_handle(handle):
    closeHandle = _kernel32_dll.CloseHandle
    closeHandle.restype = c_uint
    closeHandle.errcheck = errcheck 

    result = closeHandle(handle)
    return result

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

def get_current_process_id():
    getCurrentProcId = _kernel32_dll.GetCurrentProcessId
    getCurrentProcId.restype = c_uint
    getCurrentProcId.errcheck = errcheckNoDocumentedFailure
    
    result = getCurrentProcId()
    return result

def show_pids(myPid, depth):
    depth_as_int = int(depth)
    while depth_as_int > 0:
        shared_mem = open_shared_memory(FILE_MAP_WRITE, SHARED_MEM, str(depth_as_int))
        shared_mem_ptr = map_view_of_shared_memory(shared_mem, FILE_MAP_WRITE)
        ptr_uint = cast(shared_mem_ptr, POINTER(c_uint))

        print(f'{myPid}: show_pids: depth {depth_as_int} PID = {ptr_uint[0]}')

        unmap_view_of_shared_memory(ptr_uint)
        close_handle(shared_mem)

        depth_as_int = depth_as_int - 1

def main():
    myPid = get_current_process_id()
    print(f'{myPid}: main: {sys.argv}')
    ready_event = open_event(READY_EVENT, sys.argv[1])
    resume_event = open_event(RESUME_EVENT, sys.argv[1])

    # Write my PID to my shared memory segment
    shared_mem = open_shared_memory(FILE_MAP_WRITE, SHARED_MEM, sys.argv[1])
    shared_mem_ptr = map_view_of_shared_memory(shared_mem, FILE_MAP_WRITE)
    ptr_uint = cast(shared_mem_ptr, POINTER(c_uint))
    ptr_uint[0] = myPid

    depth_as_int = int(sys.argv[1])
    if depth_as_int > 1:
        depth_as_int = depth_as_int - 1
        depth_as_str = str(depth_as_int)
        child_ready_event = create_event(READY_EVENT, depth_as_str) 
        child_resume_event = create_event(RESUME_EVENT, depth_as_str) 
        child_shared_mem = create_shared_memory(PAGE_READWRITE, SHARED_MEM, depth_as_str)
        proc = create_proc(depth_as_str)
        print(f'{myPid}: main: Created child process with PID = {proc.info.dwProcessId}')
        print(f'{myPid}: main: Handle to child process = {hex(proc.info.hProcess)}')

        close_handle(proc.info.hProcess)
        close_handle(proc.info.hThread)

        wait_result = wait_event(child_ready_event, 1000 * 5)
        if wait_result == WAIT_OBJECT_0:
            set_event(ready_event)
            wait_event(resume_event, INFINITE) 
            print(f'{myPid}: main: Got resume event')
        else:
            print(f'{myPid}: main: Timed out while waiting for child at depth {depth_as_str}')
    else:
        set_event(ready_event) 
        wait_event(resume_event, INFINITE) 
        print(f'{myPid}: main: Got resume event')
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

