from django.test import SimpleTestCase
from entries.mood import analyze_mood


class MoodAnalyzerTests(SimpleTestCase):
    def test_positive_text(self):
        self.assertGreater(analyze_mood("امروز خیلی خوب و عالی بود"), 0)

    def test_negative_text(self):
        self.assertLess(analyze_mood("خیلی خسته و ناراحت بودم"), 0)

    def test_neutral_text(self):
        self.assertEqual(analyze_mood("رفتم فروشگاه و نان خریدم"), 0.0)

    def test_empty_text(self):
        self.assertEqual(analyze_mood(""), 0.0)

    def test_mixed_text(self):
        score = analyze_mood("خوب بود ولی خسته شدم")
        self.assertGreaterEqual(score, -1.0)
        self.assertLessEqual(score, 1.0)

    def test_case_insensitive_english(self):
        self.assertEqual(analyze_mood("HAPPY"), analyze_mood("happy"))

    def test_score_bounds(self):
        self.assertGreaterEqual(analyze_mood("عالی خوب شاد"), -1.0)
        self.assertLessEqual(analyze_mood("عالی خوب شاد"), 1.0)