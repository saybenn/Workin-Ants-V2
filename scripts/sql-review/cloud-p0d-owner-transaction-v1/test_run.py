import unittest

import run


class ClosedObserverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        renewal, modules = run.mechanism()
        cls.source = modules[0].S
        cls.owner = run.owner_type(renewal, modules)

    def test_closed_psql_result_reaches_strict_bytes_decoder(self):
        text = '{"status":"closed","count":1}\n'

        class Observer:
            def closed_sql(self, path):
                if path != run.OBSERVE_SQL:
                    raise AssertionError(path)
                return text

        with self.assertRaisesRegex(self.source.Held, "JSON_SIZE"):
            self.source.unique_json(text)
        self.assertEqual(self.owner.closed_record(Observer(), run.OBSERVE_SQL), {"status": "closed", "count": 1})

    def test_conversion_preserves_strict_duplicate_rejection(self):
        class Observer:
            def closed_sql(self, _):
                return '{"count":1,"count":2}\n'

        with self.assertRaises(self.source.Held):
            self.owner.closed_record(Observer(), run.OBSERVE_SQL)
