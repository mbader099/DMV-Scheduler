import unittest

import app


class RestApiTests(unittest.TestCase):
    def setUp(self):
        self.app = app.app

    def test_date_validation(self):
        response = self.app.post("/appointmentSearch", data=dict(startdate="2021-07-19", enddate="2021-07-18", svcType="all_transactions", locations=[]))
        self.assertEqual(response.status.code, 400)


if __name__ == '__main__':
    unittest.main()
