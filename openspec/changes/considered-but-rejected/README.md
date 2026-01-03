# Considered But Rejected OpenSpec Changes

This directory contains OpenSpec change proposals that were **carefully considered but ultimately rejected** after engineering review.

## Purpose

These proposals are preserved because they:
- ✅ Represent **thoughtful engineering solutions**
- ✅ May become **relevant in the future** as the project scales
- ✅ Document **decision-making rationale** for future reference
- ✅ Prevent **re-proposing the same ideas** without context

## Not a Graveyard

Proposals here are **not bad ideas** - they are:
- Well-designed solutions to problems we don't have yet
- Patterns borrowed from larger-scale systems
- Premature optimizations for current project needs
- Future-looking infrastructure that may be valuable later

## Review Process

Each rejected proposal includes a `REJECTION_RATIONALE.md` file documenting:
1. **Why it was rejected** - What made it inappropriate for current scale
2. **What we did instead** - Simpler alternatives that solved the same problems
3. **When to reconsider** - Specific triggers that would make the proposal valuable
4. **Lessons learned** - Engineering principles applied in the decision

## When to Reconsider

Periodically review these proposals when:
- Project scale increases significantly (10x users, data, complexity)
- New requirements emerge (compliance, multi-environment, etc.)
- Pain points develop that match the problems these proposals solve
- Team size or deployment model changes

## Current Rejected Proposals

### 2026-01-03-duckdb-migration-system
**Summary**: External migration system with SQL files and API endpoints

**Rejected Because**: DuckDB is embedded - current automatic migrations are more appropriate at this scale (4 migrations)

**Reconsider When**:
- Migration count exceeds 10
- Multi-environment deployment needed (dev/staging/prod)
- Separate ops team handles migrations
- Compliance requires migration audit trail

**Quality**: ⭐⭐⭐⭐⭐ (excellent design, premature for current needs)

---

## Guidelines for Future Proposals

Before proposing similar changes, check this directory to see if:
1. The idea has been considered before
2. The rejection triggers still apply
3. The project has evolved enough to warrant reconsideration

## Archive Structure

```
considered-but-rejected/
├── README.md (this file)
└── YYYY-MM-DD-proposal-name/
    ├── REJECTION_RATIONALE.md (required - explains decision)
    ├── proposal.md (original proposal)
    ├── tasks.md (implementation plan)
    └── specs/ (technical specifications)
```

## Philosophy

> "The best code is code you don't write. Keep it simple until complexity is justified by actual needs."

These rejected proposals remind us to:
- **Scale appropriately** - Adopt patterns when they solve real problems
- **Measure twice, cut once** - Deeply understand the problem before building solutions
- **YAGNI** - You Aren't Gonna Need It (until you actually do)
- **Keep receipts** - Document why decisions were made for future context

---

**Note**: If you're reviewing a rejected proposal and believe conditions have changed to warrant reconsideration, create a new proposal that:
1. References the original rejected proposal
2. Explains what has changed since rejection
3. Demonstrates that the rejection triggers are now met
4. Updates the implementation plan for current project state
