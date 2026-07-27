from __future__ import annotations

import unittest

from app import _friendly_error_message
from chart import PLACE_HINT, PlaceLookupError


class FriendlyErrorTests(unittest.TestCase):
    def test_place_lookup_uses_hint(self) -> None:
        msg = _friendly_error_message(PlaceLookupError("boom 400"), kind="place")
        self.assertEqual(msg, PLACE_HINT)
        self.assertIn("Shaanxi", msg)

    def test_rate_limit_and_server_down(self) -> None:
        self.assertIn("稍候", _friendly_error_message("Error code: 429 - rate limit"))
        self.assertIn("晚安", _friendly_error_message("HTTP 502 Bad Gateway"))

    def test_generic_api_400(self) -> None:
        self.assertIn("频繁", _friendly_error_message("Error code: 400 - bad request"))


if __name__ == "__main__":
    unittest.main()
