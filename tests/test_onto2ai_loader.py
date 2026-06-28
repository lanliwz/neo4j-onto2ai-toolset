import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from rdflib import Graph

from neo4j_onto2ai_toolset import onto2ai_loader
from neo4j_onto2ai_toolset.onto2ai_core import base_functions


class OntologyLoaderTests(unittest.TestCase):
    def test_load_ontology_tracks_loaded_and_processed_iris_separately(self):
        root_iri = "http://example.com/root"
        missing_iri = "http://example.com/missing"
        root_turtle = f"""
            @prefix owl: <http://www.w3.org/2002/07/owl#> .
            <{root_iri}> a owl:Ontology ;
                owl:imports <{missing_iri}> .
        """

        original_get_rdf_data = onto2ai_loader.get_rdf_data

        def fake_get_rdf_data(uri, local_only=False):
            if uri == root_iri:
                return root_turtle
            raise FileNotFoundError(uri)

        onto2ai_loader.get_rdf_data = fake_get_rdf_data
        try:
            graph = Graph()
            loaded = set()
            processed = set()
            failed = []

            onto2ai_loader.load_ontology_with_imports(
                graph,
                root_iri,
                format="turtle",
                imported_set=loaded,
                processed_set=processed,
                failed_uris=failed,
                local_files_only=True,
            )
        finally:
            onto2ai_loader.get_rdf_data = original_get_rdf_data

        self.assertEqual(loaded, {root_iri})
        self.assertEqual(processed, {root_iri, missing_iri})
        self.assertEqual(len(failed), 1)
        self.assertEqual(failed[0]["uri"], missing_iri)
        self.assertEqual(failed[0]["stage"], "fetch")

    def test_get_rdf_data_raises_when_local_file_is_missing(self):
        original_root = base_functions.ONTO_ROOT
        with tempfile.TemporaryDirectory() as temp_dir:
            base_functions.ONTO_ROOT = temp_dir
            try:
                with self.assertRaises(FileNotFoundError):
                    base_functions.get_rdf_data(
                        "http://example.com/missing", local_only=True
                    )
            finally:
                base_functions.ONTO_ROOT = original_root

    def test_load_parser_accepts_local_files_only(self):
        args = onto2ai_loader.build_parser().parse_args(
            ["load", "--uri", "http://example.com/root", "--local-files-only"]
        )

        self.assertEqual(args.command, "load")
        self.assertTrue(args.local_files_only)

    def test_load_neo4j_db_skips_store_write_when_root_fails(self):
        original_load_ontology = onto2ai_loader.load_ontology_with_imports
        root_iri = "http://example.com/root"
        failed = []

        def fake_load_ontology(
            graph,
            uri,
            *,
            format=None,
            imported_set=None,
            processed_set=None,
            failed_uris=None,
            local_files_only=False,
        ):
            if processed_set is not None:
                processed_set.add(uri)
            if failed_uris is not None:
                failed_uris.append(
                    {"uri": uri, "stage": "fetch", "error": "not found"}
                )

        onto2ai_loader.load_ontology_with_imports = fake_load_ontology
        try:
            onto2ai_loader.load_neo4j_db(
                root_iri,
                "application/rdf+xml",
                imported_set=set(),
                processed_set=set(),
                failed_uris=failed,
                local_files_only=True,
            )
        finally:
            onto2ai_loader.load_ontology_with_imports = original_load_ontology

        self.assertEqual(failed[0]["uri"], root_iri)

    def test_root_load_failure_marks_run_failed_in_history(self):
        original_get_config = onto2ai_loader.get_neo4j_model_config
        original_load_neo4j_db = onto2ai_loader.load_neo4j_db

        root_iri = "http://example.com/root"

        def fake_get_config():
            return SimpleNamespace(
                url="bolt://example.invalid:7687",
                database="testdb",
                username="neo4j",
            )

        def fake_load_neo4j_db(
            onto_uri,
            rdf_format,
            *,
            discover=False,
            imported_set=None,
            processed_set=None,
            failed_uris=None,
            local_files_only=False,
        ):
            if processed_set is not None:
                processed_set.add(onto_uri)
            if failed_uris is not None:
                failed_uris.append(
                    {"uri": onto_uri, "stage": "fetch", "error": "not found"}
                )

        onto2ai_loader.get_neo4j_model_config = fake_get_config
        onto2ai_loader.load_neo4j_db = fake_load_neo4j_db

        with tempfile.TemporaryDirectory() as temp_dir:
            history_path = Path(temp_dir) / "history.json"
            try:
                with self.assertRaises(RuntimeError):
                    onto2ai_loader.execute_loader_run(
                        selection=[root_iri],
                        rdf_format="application/rdf+xml",
                        discover_mode=True,
                        do_reset=False,
                        do_materialize=False,
                        do_cleanup=False,
                        history_path=history_path,
                        local_files_only=True,
                    )
            finally:
                onto2ai_loader.get_neo4j_model_config = original_get_config
                onto2ai_loader.load_neo4j_db = original_load_neo4j_db

            history = json.loads(history_path.read_text(encoding="utf-8"))

        run = history["runs"][0]
        self.assertEqual(run["status"], "failed")
        self.assertEqual(run["loaded_ontology_count"], 0)
        self.assertEqual(run["processed_ontology_count"], 1)
        self.assertEqual(run["failed_ontology_count"], 1)


if __name__ == "__main__":
    unittest.main()
