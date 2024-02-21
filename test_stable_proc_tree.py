import unittest

import stable_proc_tree

class StableProcTreeTestCases(unittest.TestCase):
    def test_create_proc(self):
        proc = stable_proc_tree.create_proc()
        self.assertIsNotNone(proc)

        print(f'PID = {proc.info.dwProcessId}')
        print(f'Proc handle = {hex(proc.info.hProcess)}')

        result = proc.wait_to_exit()
        self.assertEqual(result, stable_proc_tree.WAIT_TIMEOUT)

        result, last_error = proc.terminate()
        self.assertTrue(result)

        result = proc.wait_to_exit()
        #self.assertEqual(result, stable_proc_tree.WAIT_OBJECT_0)
