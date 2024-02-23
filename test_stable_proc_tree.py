from ctypes import cast
from ctypes import c_uint
from ctypes import POINTER
import time
import unittest

import stable_proc_tree

class StableProcTreeTestCases(unittest.TestCase):
    def test_create_proc(self):
        depth = "2"

        myPid = stable_proc_tree.get_current_process_id()

        child_ready_event = stable_proc_tree.create_event(stable_proc_tree.READY_EVENT, depth)
        child_resume_event = stable_proc_tree.create_event(stable_proc_tree.RESUME_EVENT, depth)
        child_shared_mem = stable_proc_tree.create_shared_memory(stable_proc_tree.PAGE_READWRITE,
            stable_proc_tree.SHARED_MEM, depth)

        proc = stable_proc_tree.create_proc(depth)
        self.assertIsNotNone(proc)

        print(f'{myPid}: UT: Created child process with PID = {proc.info.dwProcessId}')
        print(f'{myPid}: UT: Handle to child process = {hex(proc.info.hProcess)}')

        stable_proc_tree.close_handle(proc.info.hProcess)
        stable_proc_tree.close_handle(proc.info.hThread)

        wait_result = stable_proc_tree.wait_event(child_ready_event, 1000 * 5)
        self.assertEqual(wait_result, stable_proc_tree.WAIT_OBJECT_0)

        # All processes in the tree have signalled that they are ready

        stable_proc_tree.show_pids(myPid, depth)

        #time.sleep(3)
        # resume grand child
        grand_child_resume_event = stable_proc_tree.open_event(stable_proc_tree.RESUME_EVENT, "1")
        stable_proc_tree.set_event(grand_child_resume_event)

        #time.sleep(5)
        # resume child
        stable_proc_tree.set_event(child_resume_event)

        #result = proc.wait_to_exit()
        #self.assertEqual(result, stable_proc_tree.WAIT_TIMEOUT)

        #result, last_error = proc.terminate()
        #self.assertTrue(result)

        #result = proc.wait_to_exit()
        #self.assertEqual(result, stable_proc_tree.WAIT_OBJECT_0)
