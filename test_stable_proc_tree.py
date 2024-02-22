import time
import unittest

import stable_proc_tree

class StableProcTreeTestCases(unittest.TestCase):
    def test_create_proc(self):
        depth = "2"

        child_ready_event = stable_proc_tree.create_event(stable_proc_tree.READY_EVENT, depth)
        d2_child_resume_event = stable_proc_tree.create_event(stable_proc_tree.RESUME_EVENT, depth)

        proc = stable_proc_tree.create_proc(depth)
        self.assertIsNotNone(proc)

        print(f'PID = {proc.info.dwProcessId}')
        print(f'Proc handle = {hex(proc.info.hProcess)}')

        wait_result = stable_proc_tree.wait_event(child_ready_event, 1000 * 5)
        self.assertEqual(wait_result, stable_proc_tree.WAIT_OBJECT_0)

        # All processes in the tree have signalled that they are ready

        time.sleep(3)
        d1_child_resume_event = stable_proc_tree.open_event(stable_proc_tree.RESUME_EVENT, "1")
        stable_proc_tree.set_event(d1_child_resume_event)

        time.sleep(5)
        stable_proc_tree.set_event(d2_child_resume_event)

        #result = proc.wait_to_exit()
        #self.assertEqual(result, stable_proc_tree.WAIT_TIMEOUT)

        #result, last_error = proc.terminate()
        #self.assertTrue(result)

        #result = proc.wait_to_exit()
        #self.assertEqual(result, stable_proc_tree.WAIT_OBJECT_0)
