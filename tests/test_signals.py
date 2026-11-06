import unittest

import numpy as np

import moe_lstm


class SignalTests(unittest.TestCase):
    def test_positions_are_long_or_flat(self):
        positions = moe_lstm.study_positions([1, 0, 1])
        self.assertTrue(np.array_equal(positions, np.array([1.0, 0.0, 1.0])))

    def test_engine_weights_match_the_flat_position(self):
        self.assertEqual(moe_lstm.long_only_target_weights([1, 0, 1]), ["1", "0", "1"])

    def test_bad_predictions_are_rejected(self):
        with self.assertRaises(ValueError):
            moe_lstm.study_positions([])
        with self.assertRaises(ValueError):
            moe_lstm.long_only_target_weights([2])
