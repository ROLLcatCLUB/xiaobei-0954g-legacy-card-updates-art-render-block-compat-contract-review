# 0954G Legacy Card Updates To Art Render Block Compatibility Contract Report

## Stage

- stage_id: `0954G_LEGACY_CARD_UPDATES_TO_ART_RENDER_BLOCK_COMPATIBILITY_CONTRACT`
- stage_type: `legacy_card_updates_to_art_render_block_compatibility_contract_only`
- previous_stage: `0954F_ART_SUBJECT_PACK_INACTIVE_SMOKE`
- previous_status: `ART_SUBJECT_PACK_INACTIVE_SMOKE_PASS`
- final_status: `LEGACY_CARD_UPDATES_ART_RENDER_BLOCK_COMPAT_CONTRACT_PASS`
- recommended_next_stage: `0954H_LEGACY_CARD_UPDATES_ART_RENDER_BLOCK_INACTIVE_APPLY`

## Purpose

0954G defines the compatibility contract for old workbench `card_updates`, 0952F twelve-card output, and the 0952G provider candidate patch to enter the new art subject-pack + 0954C render block expression.

The intended compatibility expression is:

```text
card_updates -> legacy_card_block
0952F 12 cards -> art legacy_card_block sequence
0952G provider candidate patch -> candidate_patch_block
art subject pack context -> inactive_art_render_plan
```

## Boundary

This is a contract-only stage. It does not implement a runtime adapter, does not change `componentGrid`, does not import compatibility code into the existing workbench runtime, and does not modify `frontend/workbench/index.html`, existing frontend runtime files, backend files, endpoints, provider code, memory, Feishu, scoring, export, deploy, or seal state.

0952F and 0952G source files are not moved or deleted.

## Inputs And Outputs

Inputs defined:

- `card_updates[]`
- 0952F twelve-card fixture
- 0952G provider candidate patch fixture
- art subject pack qinglv topic context
- 0954C render block schema

Outputs defined:

- `legacy_card_block[]`
- `candidate_patch_block`
- `status_summary_block`
- `review_gate_block`
- `inactive_art_render_plan`

## Field Mapping Summary

The contract maps:

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

## Sample Output Summary

`compatibility/card_updates/legacy_card_updates_sample_output_0954G.json` contains:

- 12 `legacy_card_block` entries from the 0952F card sequence.
- 1 `candidate_patch_block` from the 0952G provider candidate patch.
- 1 `review_gate_block` for teacher confirmation.
- 1 `status_summary_block`.
- 1 `inactive_art_render_plan` using the art subject pack qinglv context.

The sample is declarative and inactive. It does not execute actions or call provider/backend/memory/Feishu.

## Legacy Strategy

`legacy_card_block` is compatibility-only. New platform core output should prefer finer-grained render blocks when it is no longer representing old card surfaces.

The next stage may implement an inactive adapter only. A smoke stage must follow before any runtime integration decision.

## Validation

Expected validator success stdout:

```text
ALL_0954G_LEGACY_CARD_UPDATES_ART_RENDER_BLOCK_COMPATIBILITY_CONTRACT_CHECKS_OK
```
