import unittest

from scheduler import Scheduler


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.scheduler = Scheduler()

    def test_empty_locations(self):
        self.assertEqual([], self.scheduler.searchForAppointments([], None, None))


if __name__ == '__main__':
    unittest.main()
