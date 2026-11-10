import unittest

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".claude/skills/job-search-copilot/scripts"))

from rank_jobs import rank_jobs, score_job


class RankJobsTests(unittest.TestCase):
    def setUp(self):
        self.profile = {
            "skills": ["Python", "SQL", "Power BI", "Stakeholder Management"],
            "target_locations": ["Zurich"],
            "remote_preference": "remote_or_hybrid",
        }

    def test_score_matches_required_preferred_and_location(self):
        result = score_job(self.profile, {
            "title": "Data Analyst",
            "company": "Example AG",
            "location": "Zurich, Switzerland",
            "work_mode": "hybrid",
            "required_skills": ["python", "SQL"],
            "preferred_skills": ["Power BI", "Tableau"],
        })
        self.assertEqual(result["fit_score"], 89.4)
        self.assertEqual(result["missing_required_skills"], [])
        self.assertEqual(result["missing_preferred_skills"], ["Tableau"])

    def test_remote_only_rejects_onsite_location(self):
        profile = {"skills": ["Python"], "remote_preference": "remote_only"}
        result = score_job(profile, {
            "required_skills": ["Python"],
            "work_mode": "onsite",
        })
        self.assertEqual(result["location_score"], 0.0)
        self.assertEqual(result["fit_score"], 85.0)

    def test_no_skills_data_marks_job_unscored(self):
        result = score_job({"skills": ["Python"]}, {"title": "Analyst"})
        self.assertIsNone(result["fit_score"])
        self.assertEqual(result["status"], "insufficient_data")

    def test_normalization_handles_case_and_accents(self):
        result = score_job({"skills": ["communication"]}, {
            "required_skills": ["COMMUNICATION"],
        })
        self.assertEqual(result["fit_score"], 100.0)

    def test_rank_orders_highest_match_first(self):
        jobs = [
            {"title": "Low", "required_skills": ["Java"]},
            {"title": "High", "required_skills": ["Python", "SQL"]},
        ]
        results = rank_jobs({"skills": ["Python", "SQL"]}, jobs)
        self.assertEqual(results[0]["title"], "High")

    def test_invalid_preference_is_rejected(self):
        with self.assertRaises(ValueError):
            score_job({"skills": ["Python"], "remote_preference": "anywhere"}, {
                "required_skills": ["Python"],
            })

    def test_remote_job_with_unspecified_country_stays_unknown(self):
        result = score_job(self.profile, {
            "required_skills": ["Python"],
            "work_mode": "remote",
            "location": "Remote",
        })
        self.assertEqual(result["location_score"], 50.0)

    def test_matching_city_does_not_override_incompatible_remote_preference(self):
        result = score_job({
            "skills": ["Python"],
            "target_locations": ["Zurich"],
            "remote_preference": "remote_only",
        }, {
            "required_skills": ["Python"],
            "work_mode": "onsite",
            "location": "Zurich, Switzerland",
        })
        self.assertEqual(result["location_score"], 0.0)
        self.assertEqual(result["fit_score"], 85.0)

    def test_bad_skill_field_is_rejected(self):
        with self.assertRaises(ValueError):
            score_job({"skills": "Python"}, {"required_skills": ["Python"]})


if __name__ == "__main__":
    unittest.main()