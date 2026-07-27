"""Tests for anonymous usage / section feedback counters."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from usage_stats import (
    get_section_feedback_counts,
    get_usage_stats,
    record_section_feedback,
    record_successful_report,
)


class UsageStatsTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.db = Path(self._tmp.name) / "usage.sqlite"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_record_and_read_usage(self) -> None:
        record_successful_report(has_question=True, db_path=self.db)
        record_successful_report(has_question=False, db_path=self.db)
        stats = get_usage_stats(db_path=self.db, total_base=10, question_base=3)
        self.assertEqual(stats.total, 12)
        self.assertEqual(stats.with_question, 4)
        self.assertEqual(stats.without_question, 1)

    def test_section_feedback_increments(self) -> None:
        record_section_feedback(section=1, hit=True, db_path=self.db)
        record_section_feedback(section=1, hit=True, db_path=self.db)
        record_section_feedback(section=1, hit=False, db_path=self.db)
        hit, miss = get_section_feedback_counts(1, db_path=self.db)
        self.assertEqual(hit, 2)
        self.assertEqual(miss, 1)

    def test_invalid_section_ignored(self) -> None:
        record_section_feedback(section=6, hit=True, db_path=self.db)
        hit, miss = get_section_feedback_counts(6, db_path=self.db)
        self.assertEqual((hit, miss), (0, 0))


if __name__ == "__main__":
    unittest.main()
