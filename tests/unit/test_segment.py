import unittest

from core.segment import Segment

class DummyTrain:
    """A simple dummy object to represent a train."""
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"DummyTrain({self.name})"

class TestSegment(unittest.TestCase):
    def setUp(self):
        self.segment = Segment("segment1")
        self.train1 = DummyTrain("A")
        self.train2 = DummyTrain("B")

    def test_empty_segment_accepts_entry(self):
        result = self.segment.request_entry(self.train1)
        self.assertTrue(result)
        self.assertEqual(self.segment.occupied_by, self.train1)

    def test_segment_denies_entry_to_another_train(self):
        self.segment.request_entry(self.train1)
        result = self.segment.request_entry(self.train2)
        self.assertFalse(result)
        self.assertEqual(self.segment.occupied_by, self.train1)

    def test_segment_allows_reentry_to_same_train(self):
        self.segment.request_entry(self.train1)
        result = self.segment.request_entry(self.train1)
        self.assertTrue(result)

    def test_leave_frees_segment(self):
        self.segment.request_entry(self.train1)
        self.segment.leave(self.train1)
        self.assertIsNone(self.segment.occupied_by)

    def test_only_occupier_can_leave(self):
        self.segment.request_entry(self.train1)
        self.segment.leave(self.train2)  # train2 should NOT be able to free the segment
        self.assertEqual(self.segment.occupied_by, self.train1)

    def test_sequence_of_occupancy(self):
        # Train1 enters and leaves, then train2 can enter
        self.assertTrue(self.segment.request_entry(self.train1))
        self.segment.leave(self.train1)
        self.assertTrue(self.segment.request_entry(self.train2))
        self.assertEqual(self.segment.occupied_by, self.train2)

if __name__ == "__main__":
    unittest.main()
