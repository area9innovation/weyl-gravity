import unittest

from .verify import main


class V6AObservationTest(unittest.TestCase):
    def test_materialized_parent_only_observation(self) -> None:
        main()
