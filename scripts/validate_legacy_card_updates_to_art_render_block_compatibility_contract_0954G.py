from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path


STAGE_ID = "0954G_LEGACY_CARD_UPDATES_TO_ART_RENDER_BLOCK_COMPATIBILITY_CONTRACT"
STAGE_TYPE = "legacy_card_updates_to_art_render_block_compatibility_contract_only"
PASS_STATUS = "LEGACY_CARD_UPDATES_ART_RENDER_BLOCK_COMPAT_CONTRACT_PASS"
NEXT_STAGE = "0954H_LEGACY_CARD_UPDATES_ART_RENDER_BLOCK_INACTIVE_APPLY"
PY_OK = "ALL_0954G_LEGACY_CARD_UPDATES_ART_RENDER_BLOCK_COMPATIBILITY_CONTRACT_CHECKS_OK"
PACKAGE_MANIFEST = "docs/audit_packages/legacy_card_updates_to_art_render_block_compatibility_contract_0954G_manifest.json"
ZIP_PATH = "docs/audit_packages/legacy_card_updates_to_art_render_block_compatibility_contract_0954G.zip"

REQUIRED_FILES = [
    "compatibility/card_updates/legacy_card_updates_to_art_render_block_contract_0954G.md",
    "compatibility/card_updates/legacy_card_updates_to_art_render_block_contract_0954G.json",
    "compatibility/card_updates/legacy_card_updates_field_mapping_0954G.json",
    "compatibility/card_updates/legacy_card_updates_sample_output_0954G.json",
    "compatibility/card_updates/provider_candidate_patch_mapping_0954G.json",
    "docs/audit/legacy_card_updates_to_art_render_block_compatibility_contract_0954G_report.md",
    "docs/audit/legacy_card_updates_to_art_render_block_compatibility_contract_0954G_result.json",
    "docs/audit/legacy_card_updates_to_art_render_block_compatibility_contract_0954G_checklist.json",
    "scripts/validate_legacy_card_updates_to_art_render_block_compatibility_contract_0954G.py",
    PACKAGE_MANIFEST,
]

SOURCE_FILES = [
    "frontend/workbench/fixtures/agent_output_existing_workbench_fixture_0952F_R1.js",
    "frontend/workbench/fixtures/provider_candidate_patch_0952G_R1.js",
    "subject_packs/art/topic_contexts/qinglv_china_color_topic_context_0954E.json",
    "platform_core/render_blocks/render_block_type_schema_0954C.json",
]

MUST_BE_TRUE = [
    "compatibility_contract_created",
    "field_mapping_created",
    "sample_output_created",
    "provider_candidate_patch_mapping_created",
    "legacy_0952f_mapping_defined",
    "legacy_0952g_mapping_defined",
    "art_subject_pack_context_used",
    "render_block_schema_used",
    "legacy_card_block_compatibility_only",
]

MUST_BE_FALSE = [
    "compatibility_runtime_imported",
    "frontend_modified",
    "index_html_modified",
    "existing_frontend_runtime_modified",
    "backend_modified",
    "endpoint_created",
    "provider_called",
    "memory_read",
    "memory_write",
    "feishu_writeback",
    "formal_scoring",
    "formal_export",
    "server_deploy",
    "seal_performed",
    "seal_allowed",
]

EXPECTED_MAPPINGS = {
    ("card_id", "block_id"),
    ("card_title", "title"),
    ("teacher_visible_summary", "content.summary"),
    ("editable_fields", "content.editable_fields"),
    ("source_from_r2", "source"),
    ("status", "status"),
    ("available_actions", "actions"),
    ("candidate_patch.target_card_id", "candidate_patch_block.content.target_card_id"),
    ("proposed_teacher_visible_text", "candidate_patch_block.content.proposed_teacher_visible_text"),
    ("teacher_confirmation_required", "review_gate_block"),
}

SAFETY_FALSE = [
    "raw_html_allowed",
    "script_allowed",
    "inline_event_handler_allowed",
    "provider_call_allowed",
    "backend_call_allowed",
    "memory_write_allowed",
    "feishu_writeback_allowed",
    "formal_export_allowed",
    "seal_allowed",
]

RUNTIME_FILES_TO_SCAN = [
    "frontend/workbench/index.html",
    "frontend/workbench/workbench_dynamic_cards_v1.js",
    "frontend/workbench/workbench_agent_runtime_client_v1.js",
    "frontend/workbench/agent_output_to_existing_workbench_adapter_0952F_R1.js",
    "backend/xiaobei_ai/workbench_agent_runtime.py",
]

FORBIDDEN_RUNTIME_REFS = [
    "legacy_card_updates_to_art_render_block_contract_0954G",
    "legacy_card_updates_field_mapping_0954G",
    "legacy_card_updates_sample_output_0954G",
    "provider_candidate_patch_mapping_0954G",
]

FORBIDDEN_ZIP_PATTERNS = [
    re.compile(r"(^|/)\.env($|[./_-])", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"student[_-]?private", re.IGNORECASE),
    re.compile(r"真实学生数据"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=None)
    return parser.parse_args()


def get_root() -> Path:
    args = parse_args()
    if args.root:
        return Path(args.root).resolve()
    return Path(__file__).resolve().parents[1]


ROOT = get_root()


def read_json(relative_path: str) -> dict:
    with (ROOT / relative_path).open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise AssertionError(f"{relative_path} must contain a JSON object")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_newlines(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def bytes_match_manifest(path: Path, expected_sha: str, expected_size: int) -> bool:
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() == expected_sha and len(data) == expected_size:
        return True
    normalized = normalize_newlines(data)
    return hashlib.sha256(normalized).hexdigest() == expected_sha


def assert_files_exist() -> None:
    for relative_path in [*REQUIRED_FILES, *SOURCE_FILES]:
        if not (ROOT / relative_path).is_file():
            raise AssertionError(f"missing file: {relative_path}")
    if not (ROOT / ZIP_PATH).is_file():
        raise AssertionError(f"missing zip: {ZIP_PATH}")


def assert_result() -> None:
    result = read_json("docs/audit/legacy_card_updates_to_art_render_block_compatibility_contract_0954G_result.json")
    if result.get("stage_id") != STAGE_ID:
        raise AssertionError("stage_id mismatch")
    if result.get("stage_type") != STAGE_TYPE:
        raise AssertionError("stage_type mismatch")
    if result.get("previous_stage") != "0954F_ART_SUBJECT_PACK_INACTIVE_SMOKE":
        raise AssertionError("previous_stage mismatch")
    if result.get("previous_status") != "ART_SUBJECT_PACK_INACTIVE_SMOKE_PASS":
        raise AssertionError("previous_status mismatch")
    for key in MUST_BE_TRUE:
        if result.get(key) is not True:
            raise AssertionError(f"{key} must be true")
    for key in MUST_BE_FALSE:
        if result.get(key) is not False:
            raise AssertionError(f"{key} must be false")
    if result.get("final_status") != PASS_STATUS:
        raise AssertionError("final_status mismatch")
    if result.get("recommended_next_stage") != NEXT_STAGE:
        raise AssertionError("recommended_next_stage mismatch")


def assert_contract() -> None:
    contract = read_json("compatibility/card_updates/legacy_card_updates_to_art_render_block_contract_0954G.json")
    if contract.get("stage_id") != STAGE_ID:
        raise AssertionError("contract stage_id mismatch")
    if contract.get("runtime_adapter_implemented") is not False:
        raise AssertionError("runtime adapter must not be implemented")
    if contract.get("component_grid_behavior_changed") is not False:
        raise AssertionError("componentGrid behavior must not change")
    for expected in [
        "card_updates[]",
        "frontend/workbench/fixtures/agent_output_existing_workbench_fixture_0952F_R1.js",
        "frontend/workbench/fixtures/provider_candidate_patch_0952G_R1.js",
        "subject_packs/art/topic_contexts/qinglv_china_color_topic_context_0954E.json",
        "platform_core/render_blocks/render_block_type_schema_0954C.json",
    ]:
        if expected not in contract.get("inputs", []):
            raise AssertionError(f"contract input missing: {expected}")
    for expected in ["legacy_card_block[]", "candidate_patch_block", "status_summary_block", "review_gate_block", "inactive_art_render_plan"]:
        if expected not in contract.get("outputs", []):
            raise AssertionError(f"contract output missing: {expected}")
    strategy = contract.get("legacy_strategy", {})
    if strategy.get("legacy_card_block_compatibility_only") is not True:
        raise AssertionError("legacy_card_block must be compatibility only")
    if strategy.get("legacy_0952f_files_moved") is not False or strategy.get("legacy_0952g_files_moved") is not False:
        raise AssertionError("0952F/0952G files must not be moved")
    assert_safety(contract.get("safety_rules", {}), "contract safety")


def assert_safety(safety: dict, label: str) -> None:
    for key in SAFETY_FALSE:
        if safety.get(key) is not False:
            raise AssertionError(f"{label} {key} must be false")


def assert_field_mapping() -> None:
    mapping = read_json("compatibility/card_updates/legacy_card_updates_field_mapping_0954G.json")
    pairs = {(item.get("input"), item.get("output")) for item in mapping.get("field_mappings", [])}
    missing = EXPECTED_MAPPINGS - pairs
    if missing:
        raise AssertionError(f"field mappings missing: {sorted(missing)}")
    for block_type in ["legacy_card_block", "candidate_patch_block", "status_summary_block", "review_gate_block", "inactive_art_render_plan"]:
        if block_type not in mapping.get("required_output_blocks", []):
            raise AssertionError(f"required output block missing: {block_type}")
    assert_safety(mapping.get("safety_rules", {}), "field mapping safety")


def assert_provider_mapping() -> None:
    mapping = read_json("compatibility/card_updates/provider_candidate_patch_mapping_0954G.json")
    if mapping.get("target_block_type") != "candidate_patch_block":
        raise AssertionError("provider mapping target block mismatch")
    if mapping.get("provider_fixture_note", {}).get("0954g_provider_called") is not False:
        raise AssertionError("0954G must not call provider")
    pairs = {(item.get("input"), item.get("output")) for item in mapping.get("field_mappings", [])}
    for expected in [
        ("target_card_id", "candidate_patch_block.content.target_card_id"),
        ("proposed_teacher_visible_text", "candidate_patch_block.content.proposed_teacher_visible_text"),
        ("teacher_confirmation_required", "review_gate_block.content.teacher_confirmation_required"),
    ]:
        if expected not in pairs:
            raise AssertionError(f"provider mapping missing: {expected}")
    assert_safety(mapping.get("safety_rules", {}), "provider mapping safety")


def assert_sample_output() -> None:
    sample = read_json("compatibility/card_updates/legacy_card_updates_sample_output_0954G.json")
    blocks = sample.get("legacy_card_blocks")
    if not isinstance(blocks, list) or len(blocks) != 12:
        raise AssertionError("sample must contain 12 legacy_card_block entries")
    for block in blocks:
        if block.get("block_type") != "legacy_card_block":
            raise AssertionError("0952F cards must map to legacy_card_block")
        if not block.get("block_id") or not block.get("title"):
            raise AssertionError("legacy_card_block missing id/title")
        content = block.get("content", {})
        if "summary" not in content or "editable_fields" not in content:
            raise AssertionError("legacy_card_block missing mapped content fields")
        assert_safety(block.get("safety", {}), f"legacy block {block.get('block_id')} safety")
    candidate = sample.get("candidate_patch_block", {})
    if candidate.get("block_type") != "candidate_patch_block":
        raise AssertionError("candidate patch must map to candidate_patch_block")
    if candidate.get("content", {}).get("target_card_id") != "qinglv_color_rule":
        raise AssertionError("candidate target_card_id mismatch")
    if not candidate.get("content", {}).get("proposed_teacher_visible_text"):
        raise AssertionError("candidate proposed text missing")
    if candidate.get("source", {}).get("provider_called_in_0954G") is not False:
        raise AssertionError("0954G provider call flag must be false")
    assert_safety(candidate.get("safety", {}), "candidate safety")
    gate = sample.get("review_gate_block", {})
    if gate.get("block_type") != "review_gate_block":
        raise AssertionError("review gate missing")
    if gate.get("content", {}).get("teacher_confirmation_required") is not True:
        raise AssertionError("teacher confirmation gate missing")
    assert_safety(gate.get("safety", {}), "review gate safety")
    status = sample.get("status_summary_block", {})
    if status.get("block_type") != "status_summary_block":
        raise AssertionError("status summary missing")
    if status.get("content", {}).get("legacy_card_block_count") != 12:
        raise AssertionError("status summary card count mismatch")
    plan = sample.get("inactive_art_render_plan", {})
    if plan.get("topic_context") != "qinglv_china_color":
        raise AssertionError("inactive art render plan topic mismatch")
    if plan.get("runtime_connected") is not False or plan.get("component_grid_behavior_changed") is not False:
        raise AssertionError("inactive art render plan must not connect runtime or change componentGrid")


def assert_sources() -> None:
    fixture = (ROOT / "frontend/workbench/fixtures/agent_output_existing_workbench_fixture_0952F_R1.js").read_text(encoding="utf-8")
    patch = (ROOT / "frontend/workbench/fixtures/provider_candidate_patch_0952G_R1.js").read_text(encoding="utf-8")
    topic = read_json("subject_packs/art/topic_contexts/qinglv_china_color_topic_context_0954E.json")
    schema = read_json("platform_core/render_blocks/render_block_type_schema_0954C.json")
    if fixture.count("[\"") < 12 or "topic_understanding" not in fixture or "next_refinement" not in fixture:
        raise AssertionError("0952F fixture does not expose expected 12 card source")
    if "provider-candidate-patch-0952G-R1-qinglv-color-rule" not in patch:
        raise AssertionError("0952G candidate patch source missing")
    if topic.get("topic_context") != "qinglv_china_color":
        raise AssertionError("art topic context mismatch")
    enum = schema.get("properties", {}).get("block_type", {}).get("enum", [])
    for block_type in ["legacy_card_block", "candidate_patch_block", "status_summary_block", "review_gate_block"]:
        if block_type not in enum:
            raise AssertionError(f"0954C schema missing block type: {block_type}")


def assert_report() -> None:
    report = (ROOT / "docs/audit/legacy_card_updates_to_art_render_block_compatibility_contract_0954G_report.md").read_text(encoding="utf-8")
    for phrase in [
        "contract-only stage",
        "does not change `componentGrid`",
        "0952F and 0952G source files are not moved or deleted",
        "legacy_card_block` is compatibility-only",
        PY_OK,
    ]:
        if phrase not in report:
            raise AssertionError(f"report missing phrase: {phrase}")


def assert_runtime_not_imported() -> None:
    for relative_path in RUNTIME_FILES_TO_SCAN:
        path = ROOT / relative_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for ref in FORBIDDEN_RUNTIME_REFS:
            if ref in text:
                raise AssertionError(f"runtime file references 0954G compatibility contract: {relative_path} -> {ref}")


def assert_zip_path_safe(name: str) -> None:
    if "\\" in name:
        raise AssertionError(f"zip path must use forward slashes: {name}")
    if name.startswith("/") or re.match(r"^[A-Za-z]:", name):
        raise AssertionError(f"zip path must be relative: {name}")
    parts = name.split("/")
    if ".." in parts or any(part == "" for part in parts):
        raise AssertionError(f"zip path must not contain empty or parent segments: {name}")
    for pattern in FORBIDDEN_ZIP_PATTERNS:
        if pattern.search(name):
            raise AssertionError(f"zip contains forbidden path pattern: {name}")


def assert_zip_manifest(expected_files: list[str]) -> None:
    manifest = read_json(PACKAGE_MANIFEST)
    if manifest.get("stage_id") != STAGE_ID:
        raise AssertionError("package manifest stage_id mismatch")
    if manifest.get("package_type") != "github_review_audit_package":
        raise AssertionError("package type mismatch")
    files = manifest.get("files")
    if not isinstance(files, list):
        raise AssertionError("package manifest files must be list")
    manifest_paths = {item.get("path") for item in files}
    expected_paths = set(expected_files)
    if manifest_paths != expected_paths:
        raise AssertionError(f"manifest paths mismatch: {sorted(manifest_paths ^ expected_paths)}")
    entries = {}
    for item in files:
        path = item.get("path")
        assert_zip_path_safe(path)
        entries[path] = item
        if path == PACKAGE_MANIFEST and item.get("sha256") == "SELF_REFERENTIAL_MANIFEST":
            continue
        full = ROOT / path
        if not bytes_match_manifest(full, item.get("sha256"), item.get("size_bytes")):
            raise AssertionError(f"manifest sha256 mismatch: {path}")
        if item.get("size_bytes") != full.stat().st_size and hashlib.sha256(normalize_newlines(full.read_bytes())).hexdigest() != item.get("sha256"):
            raise AssertionError(f"manifest size mismatch: {path}")
    with zipfile.ZipFile(ROOT / ZIP_PATH, "r") as archive:
        names = set(archive.namelist())
        for name in names:
            assert_zip_path_safe(name)
        if names != manifest_paths:
            raise AssertionError(f"zip/manifest path mismatch: {sorted(names ^ manifest_paths)}")
        for name in names:
            entry = entries[name]
            data = archive.read(name)
            if name == PACKAGE_MANIFEST and entry.get("sha256") == "SELF_REFERENTIAL_MANIFEST":
                continue
            if entry.get("sha256") != hashlib.sha256(data).hexdigest():
                raise AssertionError(f"zip sha256 mismatch: {name}")
            if entry.get("size_bytes") != len(data):
                raise AssertionError(f"zip size mismatch: {name}")
    if manifest.get("zip_self_entry_count") != len(expected_paths):
        raise AssertionError("zip_self_entry_count mismatch")


def main() -> int:
    try:
        assert_files_exist()
        assert_result()
        assert_contract()
        assert_field_mapping()
        assert_provider_mapping()
        assert_sample_output()
        assert_sources()
        assert_report()
        assert_runtime_not_imported()
        assert_zip_manifest([*REQUIRED_FILES, *SOURCE_FILES])
    except Exception as exc:
        print(f"0954G_VALIDATION_FAILED: {exc}", file=sys.stderr)
        return 1
    print(PY_OK)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
