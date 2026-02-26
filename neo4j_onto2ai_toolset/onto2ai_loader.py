from __future__ import annotations

import argparse
import json
import logging
import os
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from rdflib import Graph, Namespace, OWL
from rdflib.plugins.sparql import prepareQuery
from rdflib_neo4j import HANDLE_VOCAB_URI_STRATEGY, Neo4jStore, Neo4jStoreConfig

from neo4j_onto2ai_toolset.onto2ai_tool_config import auth_data, neo4j_model, semanticdb
from neo4j_onto2ai_toolset.onto2ai_core.base_functions import get_rdf_data, url_to_filepath
from neo4j_onto2ai_toolset.onto2ai_core.onto_db_initializer import reset_neo4j_db
from neo4j_onto2ai_toolset.onto2ai_core.prefixes import PREFIXES_CANON as prefixes
from neo4j_onto2ai_toolset.onto2ai_core.property_materializer import (
    cleanup_duplicate_relationships,
    materialize_properties,
)

logger = logging.getLogger("onto2ai-engineer")

DCTERMS = Namespace("http://purl.org/dc/terms/")

# TOP SPEC / DOMAINS
FIBO_SPEC = "https://spec.edmcouncil.org/fibo/ontology/MetadataFIBO/FIBOSpecification"
FND_DOMAIN = "https://spec.edmcouncil.org/fibo/ontology/FND/MetadataFND/FNDDomain"
BE_DOMAIN = "https://spec.edmcouncil.org/fibo/ontology/BE/MetadataBE/BEDomain"
BP_DOMAIN = "https://spec.edmcouncil.org/fibo/ontology/BP/MetadataBP/BPDomain"
FBC_DOMAIN = "https://spec.edmcouncil.org/fibo/ontology/FBC/MetadataFBC/FBCDomain"

DEFAULT_SELECTION = [FND_DOMAIN, BE_DOMAIN, BP_DOMAIN, FBC_DOMAIN]
DEFAULT_RDF_FORMAT = "application/rdf+xml"

_SELECTION_PRESETS = {
    "fibo-spec": [FIBO_SPEC],
    "fnd": [FND_DOMAIN],
    "be": [BE_DOMAIN],
    "bp": [BP_DOMAIN],
    "fbc": [FBC_DOMAIN],
    "default-domains": DEFAULT_SELECTION,
}

_DEFAULT_HISTORY_PATH = (
    Path(__file__).resolve().parents[1] / "log" / "ontology_load_history.json"
)

config = Neo4jStoreConfig(
    auth_data=auth_data,
    custom_prefixes=prefixes,
    handle_vocab_uri_strategy=HANDLE_VOCAB_URI_STRATEGY.SHORTEN,
    batching=True,
)

# Kept for backward compatibility with older callers.
imported_onto_set: set[str] = set()


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _iso(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


def _resolve_history_path(path_value: str | None) -> Path:
    env_override = path_value or ""
    if not env_override:
        env_override = os.environ.get("ONTO2AI_LOADER_HISTORY_PATH", "").strip()
    path = Path(env_override).expanduser() if env_override else _DEFAULT_HISTORY_PATH
    return path


def _read_history(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "runs": []}
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if "runs" not in data or not isinstance(data["runs"], list):
        raise ValueError(f"Invalid history file format: {path}")
    data.setdefault("version", 1)
    return data


def _write_history(path: Path, history: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, sort_keys=False)
        f.write("\n")


def _append_history(path: Path, run_record: dict[str, Any]) -> None:
    history = _read_history(path)
    history["runs"].append(run_record)
    _write_history(path, history)


def _find_history_run(history: dict[str, Any], run_id: str) -> dict[str, Any] | None:
    for run in history.get("runs", []):
        if run.get("run_id") == run_id:
            return run
    return None


def _resolve_selection(preset: str | None, uris: list[str] | None) -> list[str]:
    if uris:
        return uris
    if preset:
        if preset not in _SELECTION_PRESETS:
            raise ValueError(f"Unknown preset '{preset}'.")
        return list(_SELECTION_PRESETS[preset])
    return list(DEFAULT_SELECTION)


def load_ontology_with_imports(
    graph: Graph,
    uri: str,
    *,
    format: str | None = None,
    imported_set: set[str] | None = None,
    failed_uris: list[dict[str, str]] | None = None,
    local_files_only: bool = False,
) -> None:
    """Load an ontology and recursively load owl:imports."""
    target_imports = imported_set if imported_set is not None else imported_onto_set
    uri_str = str(uri)

    if uri_str in target_imports:
        return

    logger.info("Loading ontology %s", uri_str)
    target_imports.add(uri_str)

    try:
        rdf_data = get_rdf_data(uri_str, local_only=local_files_only)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to fetch RDF data for %s: %s", uri_str, exc)
        if failed_uris is not None:
            fetch_error = {"uri": uri_str, "stage": "fetch", "error": str(exc)}
            if local_files_only:
                fetch_error["local_file_path"] = url_to_filepath(uri_str)
            failed_uris.append(fetch_error)
        return

    formats_to_try = [format] if format else [None, "application/rdf+xml", "xml", "turtle", "n3", "json-ld"]

    parse_error: Exception | None = None
    for fmt in formats_to_try:
        try:
            if fmt is None:
                graph.parse(data=rdf_data)
            else:
                graph.parse(data=rdf_data, format=fmt)
            parse_error = None
            break
        except Exception as exc:  # noqa: BLE001
            parse_error = exc

    if parse_error is not None:
        logger.warning("Failed to parse ontology %s: %s", uri_str, parse_error)
        if failed_uris is not None:
            failed_uris.append({"uri": uri_str, "stage": "parse", "error": str(parse_error)})
        return

    for _, _, imported_uri in graph.triples((None, OWL.imports, None)):
        load_ontology_with_imports(
            graph,
            str(imported_uri),
            format=format,
            imported_set=target_imports,
            failed_uris=failed_uris,
            local_files_only=local_files_only,
        )


def discover_and_load_parts(
    graph: Graph,
    root_uri: str,
    *,
    format: str | None = None,
    imported_set: set[str] | None = None,
    failed_uris: list[dict[str, str]] | None = None,
    local_files_only: bool = False,
) -> None:
    """Load ontology and recursively discover all dcterms:hasPart ontologies."""
    target_imports = imported_set if imported_set is not None else imported_onto_set

    logger.info("Starting part discovery from %s", root_uri)
    load_ontology_with_imports(
        graph,
        root_uri,
        format=format,
        imported_set=target_imports,
        failed_uris=failed_uris,
        local_files_only=local_files_only,
    )

    new_parts_found = True
    while new_parts_found:
        new_parts_found = False
        parts_to_load: set[str] = set()

        for _, _, part in graph.triples((None, DCTERMS.hasPart, None)):
            part_uri = str(part)
            if part_uri not in target_imports:
                parts_to_load.add(part_uri)

        if parts_to_load:
            logger.info("Discovered %d ontology part(s)", len(parts_to_load))
            new_parts_found = True
            for part_uri in parts_to_load:
                load_ontology_with_imports(
                    graph,
                    part_uri,
                    format=format,
                    imported_set=target_imports,
                    failed_uris=failed_uris,
                    local_files_only=local_files_only,
                )


def load_neo4j_db(
    onto_uri: str,
    format: str,
    *,
    discover: bool = False,
    imported_set: set[str] | None = None,
    failed_uris: list[dict[str, str]] | None = None,
    local_files_only: bool = False,
) -> None:
    """Load one ontology URI (plus imports/parts) into Neo4j RDF store."""
    discovery_graph = Graph()
    if discover:
        discover_and_load_parts(
            discovery_graph,
            onto_uri,
            format=format,
            imported_set=imported_set,
            failed_uris=failed_uris,
            local_files_only=local_files_only,
        )
    else:
        load_ontology_with_imports(
            discovery_graph,
            onto_uri,
            format=format,
            imported_set=imported_set,
            failed_uris=failed_uris,
            local_files_only=local_files_only,
        )

    neo4j_rdf_graph = Graph(store=Neo4jStore(config=config))
    for triple in discovery_graph:
        neo4j_rdf_graph.add(triple)
    neo4j_rdf_graph.close(True)


def load_neo4j_db_ext(sparQl: str, in_mem_graph: Graph, neo4j_graph: Graph) -> None:
    """Execute a SPARQL query over in-memory graph and write matching triples to Neo4j graph."""
    query = prepareQuery(sparQl, initNs=dict(in_mem_graph.namespaces()))
    logger.info("RDF query prepared", extra={"op": "sparql_prepare", "query": sparQl})

    for row in in_mem_graph.query(query):
        clz = row.clz
        type_class = row.datatype
        prop = row.property
        neo4j_graph.add((clz, prop, type_class))
        logger.info(
            "Datatype property discovered - %s",
            str(prop),
            extra={
                "op": "sparql_extract_datatype_property",
                "subject": str(clz),
                "predicate": str(prop),
                "datatype": str(type_class),
            },
        )


def execute_loader_run(
    *,
    selection: list[str],
    rdf_format: str,
    discover_mode: bool,
    do_reset: bool,
    do_materialize: bool,
    do_cleanup: bool,
    history_path: Path,
    reloaded_from_run_id: str | None = None,
    local_files_only: bool = False,
) -> dict[str, Any]:
    """Run ontology loader and persist a detailed history record."""
    imported_onto_set.clear()
    loaded_uris: set[str] = set()
    failed_uris: list[dict[str, str]] = []

    run_id = uuid4().hex[:12]
    started_at = _utc_now()
    started_perf = time.perf_counter()

    phase_timings: dict[str, float] = {
        "reset_seconds": 0.0,
        "load_seconds": 0.0,
        "post_load_seconds": 0.0,
    }

    run_record: dict[str, Any] = {
        "run_id": run_id,
        "started_at": _iso(started_at),
        "status": "running",
        "selection": {
            "root_iris": selection,
            "discover": discover_mode,
            "rdf_format": rdf_format,
        },
        "destination": {
            "neo4j_uri": neo4j_model.url,
            "database": neo4j_model.database,
            "username": neo4j_model.username,
        },
        "actions": {
            "reset_database": do_reset,
            "materialize_properties": do_materialize,
            "cleanup_duplicate_relationships": do_cleanup,
            "local_files_only": local_files_only,
        },
    }
    if reloaded_from_run_id:
        run_record["reloaded_from_run_id"] = reloaded_from_run_id

    try:
        if do_reset:
            t0 = time.perf_counter()
            logger.info("Resetting Neo4j database %s", neo4j_model.database)
            reset_neo4j_db()
            phase_timings["reset_seconds"] = round(time.perf_counter() - t0, 3)

        t1 = time.perf_counter()
        for uri in selection:
            load_neo4j_db(
                uri,
                rdf_format,
                discover=discover_mode,
                imported_set=loaded_uris,
                failed_uris=failed_uris,
                local_files_only=local_files_only,
            )
        phase_timings["load_seconds"] = round(time.perf_counter() - t1, 3)

        t2 = time.perf_counter()
        if do_materialize:
            materialize_properties(semanticdb, "owl__ObjectProperty")
            materialize_properties(semanticdb, "owl__DatatypeProperty")
        if do_cleanup:
            cleanup_duplicate_relationships(semanticdb)
        phase_timings["post_load_seconds"] = round(time.perf_counter() - t2, 3)

        run_record["status"] = "success"
    except Exception as exc:  # noqa: BLE001
        run_record["status"] = "failed"
        run_record["error"] = str(exc)
        logger.exception("Ontology load run failed")
        raise
    finally:
        ended_at = _utc_now()
        total_seconds = round(time.perf_counter() - started_perf, 3)

        run_record["ended_at"] = _iso(ended_at)
        run_record["duration_seconds"] = total_seconds
        run_record["phase_timings"] = phase_timings
        run_record["loaded_ontology_iris"] = sorted(loaded_uris)
        run_record["loaded_ontology_count"] = len(loaded_uris)
        run_record["failed_ontology_uris"] = failed_uris
        run_record["failed_ontology_count"] = len(failed_uris)

        _append_history(history_path, run_record)

    return run_record


def _print_load_summary(run: dict[str, Any], history_path: Path) -> None:
    print("\n=== Ontology Load Summary ===")
    print(f"Run ID: {run.get('run_id')}")
    print(f"Status: {run.get('status')}")

    dest = run.get("destination", {})
    print(
        "Destination: "
        f"{dest.get('database', 'unknown')} @ {dest.get('neo4j_uri', 'unknown')} "
        f"(user={dest.get('username', 'unknown')})"
    )

    print(f"Started: {run.get('started_at')}")
    print(f"Ended: {run.get('ended_at')}")
    print(f"Duration (seconds): {run.get('duration_seconds')}")

    timing = run.get("phase_timings", {})
    print(
        "Phase timings (seconds): "
        f"reset={timing.get('reset_seconds', 0.0)}, "
        f"load={timing.get('load_seconds', 0.0)}, "
        f"post_load={timing.get('post_load_seconds', 0.0)}"
    )

    print(f"Loaded ontology IRIs: {run.get('loaded_ontology_count', 0)}")
    print(f"Failed ontology IRIs: {run.get('failed_ontology_count', 0)}")
    print(f"History file: {history_path}")


def _print_run_detail(run: dict[str, Any], *, include_iris: bool) -> None:
    print(f"Run ID: {run.get('run_id')}")
    print(f"Status: {run.get('status')}")
    print(f"Started: {run.get('started_at')}")
    print(f"Ended: {run.get('ended_at')}")
    print(f"Duration (seconds): {run.get('duration_seconds')}")

    selection = run.get("selection", {})
    print(
        "Selection: "
        f"discover={selection.get('discover')}, "
        f"format={selection.get('rdf_format')}, "
        f"roots={len(selection.get('root_iris', []))}"
    )

    dest = run.get("destination", {})
    print(
        "Destination: "
        f"{dest.get('database', 'unknown')} @ {dest.get('neo4j_uri', 'unknown')}"
    )

    print(f"Loaded ontology count: {run.get('loaded_ontology_count', 0)}")
    print(f"Failed ontology count: {run.get('failed_ontology_count', 0)}")

    if include_iris:
        print("Loaded ontology IRIs:")
        for iri in run.get("loaded_ontology_iris", []):
            print(f"- {iri}")


def _cmd_history(history_path: Path, run_id: str | None, limit: int, include_iris: bool) -> int:
    history = _read_history(history_path)
    runs = history.get("runs", [])

    if run_id:
        run = _find_history_run(history, run_id)
        if not run:
            print(f"Run ID not found: {run_id}")
            return 1
        _print_run_detail(run, include_iris=include_iris)
        return 0

    if not runs:
        print(f"No loader history found in {history_path}")
        return 0

    print(f"History file: {history_path}")
    print(f"Total runs: {len(runs)}")
    print("Recent runs:")

    recent_runs = list(reversed(runs[-limit:]))
    for run in recent_runs:
        dest = run.get("destination", {})
        print(
            f"- {run.get('run_id')} | status={run.get('status')} "
            f"| loaded={run.get('loaded_ontology_count', 0)} "
            f"| duration={run.get('duration_seconds', 0)}s "
            f"| db={dest.get('database', 'unknown')} "
            f"| started={run.get('started_at')}"
        )
    return 0


def _cmd_reload(
    history_path: Path,
    run_id: str,
    source: str,
    do_reset: bool | None,
    do_materialize: bool | None,
    do_cleanup: bool | None,
    local_files_only: bool,
) -> int:
    history = _read_history(history_path)
    prior_run = _find_history_run(history, run_id)
    if not prior_run:
        print(f"Run ID not found: {run_id}")
        return 1

    if source == "loaded":
        selection = prior_run.get("loaded_ontology_iris", [])
        discover_mode = False
    else:
        selection = prior_run.get("selection", {}).get("root_iris", [])
        discover_mode = bool(prior_run.get("selection", {}).get("discover", True))

    if not selection:
        print(f"No ontology IRIs available to reload for run {run_id}")
        return 1

    prior_selection = prior_run.get("selection", {})
    rdf_format = prior_selection.get("rdf_format", DEFAULT_RDF_FORMAT)

    actions = prior_run.get("actions", {})
    effective_reset = actions.get("reset_database", True) if do_reset is None else do_reset
    effective_materialize = actions.get("materialize_properties", True) if do_materialize is None else do_materialize
    effective_cleanup = actions.get("cleanup_duplicate_relationships", True) if do_cleanup is None else do_cleanup
    effective_local_only = bool(actions.get("local_files_only", False)) or local_files_only

    run = execute_loader_run(
        selection=selection,
        rdf_format=rdf_format,
        discover_mode=discover_mode,
        do_reset=effective_reset,
        do_materialize=effective_materialize,
        do_cleanup=effective_cleanup,
        history_path=history_path,
        reloaded_from_run_id=run_id,
        local_files_only=effective_local_only,
    )
    _print_load_summary(run, history_path)
    return 0


def _bool_override_group(parser: argparse.ArgumentParser, flag: str, default: bool) -> None:
    group = parser.add_mutually_exclusive_group()
    group.add_argument(f"--{flag}", dest=flag, action="store_true", help=f"Enable {flag.replace('_', ' ')}")
    group.add_argument(f"--no-{flag.replace('_', '-')}", dest=flag, action="store_false", help=f"Disable {flag.replace('_', ' ')}")
    parser.set_defaults(**{flag: default})


def _optional_bool_override_group(parser: argparse.ArgumentParser, flag: str) -> None:
    group = parser.add_mutually_exclusive_group()
    group.add_argument(f"--{flag}", dest=flag, action="store_true", help=f"Enable {flag.replace('_', ' ')}")
    group.add_argument(f"--no-{flag.replace('_', '-')}", dest=flag, action="store_false", help=f"Disable {flag.replace('_', ' ')}")
    parser.set_defaults(**{flag: None})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Load and materialize ontologies into Neo4j with persistent run history.",
    )
    subparsers = parser.add_subparsers(dest="command")

    load_parser = subparsers.add_parser("load", help="Load ontologies into Neo4j")
    load_parser.add_argument(
        "--preset",
        choices=sorted(_SELECTION_PRESETS.keys()),
        default="default-domains",
        help="Predefined ontology selection",
    )
    load_parser.add_argument(
        "--uri",
        action="append",
        default=None,
        help="Ontology IRI to load (repeatable). Overrides --preset when provided.",
    )
    load_parser.add_argument(
        "--format",
        dest="rdf_format",
        default=DEFAULT_RDF_FORMAT,
        help=f"RDF format hint (default: {DEFAULT_RDF_FORMAT})",
    )
    _bool_override_group(load_parser, "discover", True)
    _bool_override_group(load_parser, "reset", True)
    _bool_override_group(load_parser, "materialize", True)
    _bool_override_group(load_parser, "cleanup", True)
    load_parser.add_argument(
        "--history-path",
        default=None,
        help=f"Path to history JSON (default: {_DEFAULT_HISTORY_PATH})",
    )
    load_parser.add_argument(
        "--print-loaded-iris",
        action="store_true",
        help="Print all loaded ontology IRIs after the run.",
    )

    history_parser = subparsers.add_parser("history", help="Show load history and loaded ontology IRIs")
    history_parser.add_argument("--history-path", default=None, help="Path to history JSON")
    history_parser.add_argument("--run-id", default=None, help="Show details for one run ID")
    history_parser.add_argument("--limit", type=int, default=20, help="Number of recent runs to list")
    history_parser.add_argument(
        "--include-iris",
        action="store_true",
        help="When using --run-id, include the full loaded ontology IRI list.",
    )

    reload_parser = subparsers.add_parser("reload", help="Reload ontologies from a prior run")
    reload_parser.add_argument("--history-path", default=None, help="Path to history JSON")
    reload_parser.add_argument("--run-id", required=True, help="Run ID to replay")
    reload_parser.add_argument(
        "--source",
        choices=["loaded", "roots"],
        default="loaded",
        help="Replay source: exact loaded IRI list or original root selection.",
    )
    reload_parser.add_argument(
        "--local-files-only",
        action="store_true",
        help="Reload using local ontology files only (never fetch from the internet).",
    )
    _optional_bool_override_group(reload_parser, "reset")
    _optional_bool_override_group(reload_parser, "materialize")
    _optional_bool_override_group(reload_parser, "cleanup")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Keep backward-compatible behavior when no subcommand is provided.
    command = args.command or "load"
    history_path = _resolve_history_path(getattr(args, "history_path", None))

    if command == "history":
        return _cmd_history(
            history_path=history_path,
            run_id=args.run_id,
            limit=args.limit,
            include_iris=args.include_iris,
        )

    if command == "reload":
        return _cmd_reload(
            history_path=history_path,
            run_id=args.run_id,
            source=args.source,
            do_reset=args.reset,
            do_materialize=args.materialize,
            do_cleanup=args.cleanup,
            local_files_only=args.local_files_only,
        )

    preset = getattr(args, "preset", "default-domains")
    uris = getattr(args, "uri", None)
    rdf_format = getattr(args, "rdf_format", DEFAULT_RDF_FORMAT)
    discover = getattr(args, "discover", True)
    do_reset = getattr(args, "reset", True)
    do_materialize = getattr(args, "materialize", True)
    do_cleanup = getattr(args, "cleanup", True)
    print_loaded_iris = getattr(args, "print_loaded_iris", False)

    selection = _resolve_selection(preset, uris)

    run = execute_loader_run(
        selection=selection,
        rdf_format=rdf_format,
        discover_mode=discover,
        do_reset=do_reset,
        do_materialize=do_materialize,
        do_cleanup=do_cleanup,
        history_path=history_path,
        local_files_only=False,
    )
    _print_load_summary(run, history_path)

    if print_loaded_iris:
        print("Loaded ontology IRIs:")
        for iri in run.get("loaded_ontology_iris", []):
            print(f"- {iri}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
