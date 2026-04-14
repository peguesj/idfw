<!-- section: Framework -->
# Schema Definitions

IDFW maintains 8 validated schema/data files that define the framework's data contracts.

## Schema Files

| File | Type | Status |
|------|------|--------|
| IDDA.schemas.json | IDEA Data Architecture | Valid |
| IDDV.schemas.json | IDEA Data Validation | Valid |
| DDD.schema.jsonc | Domain-Driven Design | Valid JSONC |
| resume.schema.json | Capability Schema | draft-2020-12 |

## Seed Data Files

| File | Purpose | Status |
|------|---------|--------|
| idfpj.seed.json | Project initialization | Valid |
| idfpj.seed.expanded.json | Expanded project data | Reconstructed |
| Additional seed files | Framework bootstrapping | Valid |

## Validation

All files pass `python3 json.load()` validation after CP-01 through CP-06 fixes:

- CP-01: Fixed IDDA.schemas.json structural errors
- CP-02: Added IDDV.schemas.json header compliance
- CP-03: Rewrote DDD.schema.jsonc as valid JSONC
- CP-04: Upgraded resume.schema.json to draft-2020-12
- CP-05: Removed JS comments from seed JSON files
- CP-06: Reconstructed corrupted idfpj.seed.expanded.json

## Schema Bridge

The `unified_framework/core/schema_bridge.py` module connects these static schemas to the runtime framework, enabling:
- Runtime validation against schemas
- Schema-driven agent configuration
- Dynamic constraint generation from schema definitions
