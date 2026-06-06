# 0954G Legacy Card Updates To Art Render Block Compatibility Contract

## Stage

- stage_id: `0954G_LEGACY_CARD_UPDATES_TO_ART_RENDER_BLOCK_COMPATIBILITY_CONTRACT`
- stage_type: `legacy_card_updates_to_art_render_block_compatibility_contract_only`
- previous_stage: `0954F_ART_SUBJECT_PACK_INACTIVE_SMOKE`
- previous_status: `ART_SUBJECT_PACK_INACTIVE_SMOKE_PASS`
- final_status: `LEGACY_CARD_UPDATES_ART_RENDER_BLOCK_COMPAT_CONTRACT_PASS`
- recommended_next_stage: `0954H_LEGACY_CARD_UPDATES_ART_RENDER_BLOCK_INACTIVE_APPLY`

## Purpose

This contract defines how old workbench `card_updates`, the 0952F twelve-card fixture, and the 0952G provider candidate patch fixture can be represented by `subject_packs/art` plus the 0954C render block vocabulary.

The compatibility path is:

```text
card_updates -> legacy_card_block
0952F 12 cards -> art legacy_card_block sequence
0952G provider candidate patch -> candidate_patch_block
art subject pack context -> inactive_art_render_plan
```

This is a compatibility contract only. It does not implement a runtime adapter, does not change `componentGrid`, and does not import the compatibility layer into the existing workbench runtime.

## Compatibility Inputs

The contract accepts these inactive inputs:

1. `card_updates[]`
2. 0952F twelve-card fixture: `frontend/workbench/fixtures/agent_output_existing_workbench_fixture_0952F_R1.js`
3. 0952G provider candidate patch fixture: `frontend/workbench/fixtures/provider_candidate_patch_0952G_R1.js`
4. Art subject pack qinglv topic context: `subject_packs/art/topic_contexts/qinglv_china_color_topic_context_0954E.json`
5. 0954C render block schema: `platform_core/render_blocks/render_block_type_schema_0954C.json`

## Compatibility Outputs

The contract defines these inactive outputs:

1. `legacy_card_block[]`
2. `candidate_patch_block`
3. `status_summary_block`
4. `review_gate_block`
5. `inactive_art_render_plan`

## Field Mapping

Required field mapping:

- `card_id -> block_id`
- `card_title -> title`
- `teacher_visible_summary -> content.summary`
- `editable_fields -> content.editable_fields`
- `source_from_r2 -> source`
- `status -> block status`
- `available_actions -> actions`
- `candidate_patch.target_card_id -> candidate_patch_block.content.target_card_id`
- `proposed_teacher_visible_text -> candidate_patch_block.content.proposed_teacher_visible_text`
- `teacher_confirmation_required -> review_gate_block`

## Safety Rules

All compatibility outputs must carry these rules:

- `raw_html_allowed=false`
- `script_allowed=false`
- `inline_event_handler_allowed=false`
- `provider_call_allowed=false`
- `backend_call_allowed=false`
- `memory_write_allowed=false`
- `feishu_writeback_allowed=false`
- `formal_export_allowed=false`
- `seal_allowed=false`

## Legacy Strategy

1. `legacy_card_block` is used only for compatibility.
2. New platform core work should prefer finer-grained render blocks.
3. 0952F source files are not deleted or moved.
4. 0952G source files are not deleted or moved.
5. The compatibility layer may read fixtures to generate sample output, but must not be imported by runtime.
6. Follow-up work must first build an inactive adapter, then run an inactive smoke stage before any runtime discussion.

## Explicit Non-Goals

- No changes to `frontend/workbench/index.html`.
- No changes to existing frontend runtime.
- No backend changes.
- No endpoint creation.
- No provider call.
- No memory read/write.
- No Feishu writeback.
- No scoring/export/deploy/seal.
- No `componentGrid` behavior change.
