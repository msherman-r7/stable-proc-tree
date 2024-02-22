import unittest

import stable_proc_tree

class StableProcTreeTestCases(unittest.TestCase):
    def test_create_proc(self):
        depth = "2"

        d1_ready_event = stable_proc_tree.create_event(stable_proc_tree.READY_EVENT, depth)
        self.assertIsNotNone(d1_ready_event)

        proc = stable_proc_tree.create_proc(depth)
        self.assertIsNotNone(proc)

        print(f'PID = {proc.info.dwProcessId}')
        print(f'Proc handle = {hex(proc.info.hProcess)}')

        wait_result = stable_proc_tree.wait_event(d1_ready_event, 1000 * 5)
        self.assertEqual(wait_result, stable_proc_tree.WAIT_OBJECT_0)

        #result = proc.wait_to_exit()
        #self.assertEqual(result, stable_proc_tree.WAIT_TIMEOUT)

        #result, last_error = proc.terminate()
        #self.assertTrue(result)

        #result = proc.wait_to_exit()
        #self.assertEqual(result, stable_proc_tree.WAIT_OBJECT_0)
