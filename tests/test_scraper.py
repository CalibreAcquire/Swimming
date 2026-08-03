"""Unit tests using a constructed fixture that mimics Rightmove's known
`window.jsonModel` embed format.

IMPORTANT: this fixture is hand-written, not captured from a live response
(this project was built in a sandbox with no outbound internet access -- see
README.md). It exercises the parsing/filtering logic but does not prove the
real Rightmove page still uses this exact structure. Run
`python -m scraper.main` for real once you have network access, and update
this fixture/the extraction code in scraper/rightmove.py if it needs fixing.

Run with: python -m unittest discover -s tests
"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import filters, locations, rightmove  # noqa: E402

FIXTURE_HTML = """
<html><body>
<script>
window.jsonModel = %s;
</script>
</body></html>
""" % json.dumps(
    {
        "resultCount": "2",
        "properties": [
            {
                "id": 123456,
                "bedrooms": 3,
                "bathrooms": 1,
                "displayAddress": "1 Some Street, London",
                "propertySubType": "Detached",
                "summary": "A lovely house with a garden.",
                "price": {"amount": 450000, "displayPrices": [{"displayPrice": "£450,000"}]},
                "propertyUrl": "/properties/123456",
                "customer": {"brandTradingName": "Test Agents"},
                "location": {"latitude": 51.5, "longitude": -0.1},
                "tags": [],
            },
            {
                "id": 999,
                "bedrooms": 2,
                "bathrooms": 1,
                "displayAddress": "2 Retirement Court, Surrey",
                "propertySubType": "Retirement Property",
                "summary": "A retirement living apartment.",
                "price": {"amount": 200000},
                "propertyUrl": "/properties/999",
                "tags": ["retirement"],
            },
        ],
    }
)


class ExtractionTests(unittest.TestCase):
    def test_extract_json_payload_finds_json_model(self):
        payload = rightmove.extract_json_payload(FIXTURE_HTML)
        self.assertIn("properties", payload)

    def test_find_listing_records(self):
        payload = rightmove.extract_json_payload(FIXTURE_HTML)
        listings = rightmove.find_listing_records(payload)
        self.assertEqual(len(listings), 2)

    def test_find_result_count(self):
        payload = rightmove.extract_json_payload(FIXTURE_HTML)
        self.assertEqual(rightmove.find_result_count(payload), 2)

    def test_balanced_brace_extraction_ignores_braces_in_strings(self):
        text = 'window.jsonModel = {"a": "value with } brace", "b": 1};'
        obj = rightmove._extract_balanced_braces(text, text.index("{"))
        parsed = json.loads(obj)
        self.assertEqual(parsed["b"], 1)


class FilterTests(unittest.TestCase):
    def setUp(self):
        payload = rightmove.extract_json_payload(FIXTURE_HTML)
        self.listings = rightmove.find_listing_records(payload)

    def test_normalize_normal_listing(self):
        normalized = filters.normalize(self.listings[0], area="Greater London", channel="buy")
        self.assertEqual(normalized["id"], "123456")
        self.assertEqual(normalized["price"], 450000)
        self.assertEqual(normalized["price_display"], "£450,000")
        self.assertEqual(normalized["url"], "https://www.rightmove.co.uk/properties/123456")
        self.assertFalse(filters.is_excluded(normalized))

    def test_retirement_listing_is_excluded(self):
        normalized = filters.normalize(self.listings[1], area="Surrey", channel="buy")
        self.assertTrue(filters.is_excluded(normalized))


class LocationResolutionTests(unittest.TestCase):
    def test_extract_best_match_prefers_exact_name(self):
        payload = {
            "matches": [
                {"id": "REGION^1", "displayName": "Surrey Heath"},
                {"id": "REGION^2", "displayName": "Surrey"},
            ]
        }
        match = locations._extract_best_match(payload, "Surrey")
        self.assertEqual(match["id"], "REGION^2")

    def test_extract_best_match_generic_fallback(self):
        payload = {"weird": {"nested": [{"locationIdentifier": "REGION^3", "name": "Kent"}]}}
        match = locations._extract_best_match(payload, "Kent")
        self.assertEqual(match["locationIdentifier"], "REGION^3")


if __name__ == "__main__":
    unittest.main()
