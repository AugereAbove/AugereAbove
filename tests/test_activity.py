from datetime import date
import unittest
import xml.etree.ElementTree as ET

from scripts.build_activity import aggregate, parse_calendar, activity_svg, monthly_svg, overview_svg, languages_svg

class ActivityTests(unittest.TestCase):
    def test_counts_are_taken_from_tooltips_not_color_levels(self):
        html = '<td id="day" data-date="2026-01-01" data-level="1"></td><tool-tip for="day">1,234 contributions on January 1st.</tool-tip>'
        self.assertEqual(parse_calendar(html, date(2026, 1, 1), date(2026, 1, 1)), [{'date': '2026-01-01', 'count': 1234}])

    def test_zero_and_future_days(self):
        html = '<td id="one" data-date="2026-01-01"></td><tool-tip for="one">No contributions on January 1st.</tool-tip><td id="future" data-date="2026-01-02"></td>'
        self.assertEqual(parse_calendar(html, date(2026, 1, 1), date(2026, 1, 1))[0]['count'], 0)

    def test_missing_day_fails_instead_of_fabricating_a_zero(self):
        with self.assertRaises(ValueError):
            parse_calendar('', date(2026, 1, 1), date(2026, 1, 1))

    def test_missing_tooltip_fails_instead_of_inferring_a_count(self):
        with self.assertRaises(ValueError):
            parse_calendar('<td id="one" data-date="2026-01-01" data-level="3"></td>', date(2026, 1, 1), date(2026, 1, 1))

    def test_private_and_forked_repositories_are_excluded(self):
        public = {'private': False, 'fork': False, 'language': 'Python', 'stargazers_count': 2, 'forks_count': 1}
        result = aggregate([public, dict(public, private=True), dict(public, fork=True)])
        self.assertEqual(result, {'repositories': 1, 'stars': 2, 'forks': 1, 'languages': {'Python': 1}})

    def test_unclassified_repositories_are_counted_once(self):
        result = aggregate([{'private': False, 'fork': False, 'language': None, 'stargazers_count': 0, 'forks_count': 0}])
        self.assertEqual(result['languages'], {'Unclassified': 1})

    def test_cards_are_valid_svg_and_escape_source_labels(self):
        snapshot = {'as_of': '2026-01-01', 'days': [{'date': '2026-01-01', 'count': 2}],
                    'public_repositories': {'repositories': 1, 'stars': 0, 'forks': 0, 'languages': {'<untrusted>': 1}}}
        for renderer in [activity_svg, monthly_svg, overview_svg, languages_svg]:
            with self.subTest(renderer=renderer.__name__):
                root = ET.fromstring(renderer(snapshot))
                self.assertEqual(root.tag, '{http://www.w3.org/2000/svg}svg')
                self.assertFalse(root.findall('.//{http://www.w3.org/2000/svg}untrusted'))
                self.assertFalse(root.findall('.//{http://www.w3.org/2000/svg}script'))

if __name__ == '__main__':
    unittest.main()
