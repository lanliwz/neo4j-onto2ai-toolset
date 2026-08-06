import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from harness_config import DOMAINS, RELEASES, selected_releases
from harness_verify_dataset import verify_contract
from harness_verify_mode_boundaries import check_dataset_boundary, check_required_docs
from harness_verify_release import core_version, domain_version
from harness_verify_schema import verify_static


class HarnessConfigurationTests(unittest.TestCase):
    def test_all_registered_domains_pass_static_schema_checks(self):
        for spec in DOMAINS.values():
            with self.subTest(domain=spec.name):
                verify_static(spec)

    def test_all_registered_smoke_tests_enforce_dataset_boundaries(self):
        for spec in DOMAINS.values():
            with self.subTest(domain=spec.name):
                verify_contract(spec)

    def test_mode_contract_documents_and_registered_smoke_tests_are_enforced(self):
        check_required_docs()
        self.assertEqual(check_dataset_boundary(), len(DOMAINS))

    def test_release_versions_are_aligned(self):
        self.assertEqual(core_version(), "1.1.0")
        for name in ("entitlement", "parcel"):
            with self.subTest(package=name):
                self.assertRegex(domain_version(RELEASES[name]), r"^\d+\.\d+\.\d+$")

    def test_all_release_selection_is_complete_and_unique(self):
        selected = selected_releases(["all"])
        self.assertEqual([spec.name for spec in selected], sorted(RELEASES))


if __name__ == "__main__":
    unittest.main()
