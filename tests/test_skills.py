import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "skills"


class RepositorySkillTests(unittest.TestCase):
    def test_skill_directories_match_names_and_agent_prompts(self):
        skill_dirs = sorted(path for path in SKILLS_ROOT.iterdir() if path.is_dir())
        self.assertEqual(len(skill_dirs), 9)

        for skill_dir in skill_dirs:
            skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            name_match = re.search(r"^name:\s*([^\n]+)$", skill_text, re.MULTILINE)
            self.assertIsNotNone(name_match, skill_dir)
            skill_name = name_match.group(1).strip().strip('"')

            self.assertEqual(skill_dir.name, skill_name)

            agent_metadata = skill_dir / "agents" / "openai.yaml"
            self.assertTrue(agent_metadata.is_file(), agent_metadata)
            self.assertIn(
                f"${skill_name}",
                agent_metadata.read_text(encoding="utf-8"),
            )

    def test_skills_do_not_reference_removed_or_unimplemented_patterns(self):
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(SKILLS_ROOT.glob("*/SKILL.md"))
        )
        forbidden = {
            "PydanticNeo4jBridge",
            "SemanticModel",
            "Effective Node Label Heuristic",
            "split.js",
            "Data Properties: **DEPRECATED**",
        }

        for token in forbidden:
            self.assertNotIn(token, combined)

    def test_fibo_load_examples_are_non_destructive_by_default(self):
        skill_text = (
            SKILLS_ROOT / "load-fibo-ontology" / "SKILL.md"
        ).read_text(encoding="utf-8")
        load_commands = [
            line.strip()
            for line in skill_text.splitlines()
            if "onto2ai_loader load" in line
        ]

        self.assertGreaterEqual(len(load_commands), 2)
        self.assertTrue(all("--no-reset" in command for command in load_commands))


if __name__ == "__main__":
    unittest.main()
