# Bounded corpus checks — 2026-10-03

Latest: UCI passes all seven targets locally and in GitHub CI at 12000 MiB using the compiler
fixes published in PolyXML 031ab53. NeTEx Python passes at 3500 MiB after UPA
source deduplication, module ownership, and quoted-docstring fixes. These checks
verify compilation, not runtime XML conformance. Full validation now passes all 20 suites and the 46-module graph with the
subsequent fixes in d3ecf31; see `validation-followup/`. Detailed outcomes
and historical failures follow.

## Initial checks at 3500 MiB

Source: PolyXML 640bc40 (compiler code from v0.34.0), with C# fix a25aa49
for the later C# rerun. Exact compiler hash and tool versions are in
`verification.json`. Every generation/compile command
used MemoryMax=3500M, MemorySwapMax=0, a 600-second timeout, and serial builds.
The host had ~13.6 GiB available before checks; WSL swap remained unused.

| Module | Target | Result |
| --- | --- | --- |
| hl7_cda | Python syntax | pass |
| ubl_invoice + dependencies | Python syntax | pass |
| defense_uci (exact four-schema module) | Python, Go, TypeScript, Java | pass |
| defense_uci | C++20 syntax | pass, peak process RSS 2,753,596 KiB |
| defense_uci | C# net8.0 build | pass after Equals property-name fix |
| defense_uci | Rust cargo check, monolithic | cgroup OOM, 3.4 GiB reported scope peak |
| defense_uci | Rust cargo check, split_units=true, 250-type chunks | cgroup OOM, 25 emitted files |
| transit_netex + dependencies | Python generation | cgroup OOM (journal retained) |
| finance_fpml | Python generation/syntax | pass after adding XML-signature module dependency |

`corpus-uci-seven` includes the initial CS8866 failure; the later
`corpus-uci-csharp-fixed` log records the successful build. The Rust run failed
before C++ was reached, so C++ was checked independently. The initial FpML
failure and successful dependency fix are retained separately. These runs
predate automatic compiler SHA-256 recording in the final harness.

Harness tests passed all five tests, including a real 64 MiB kernel cap with
swap disabled, malformed-source failure retention, and timeout descendant
cleanup. The sudo/system-manager path is wired into CI but cannot be tested
locally because this machine requires interactive sudo authentication.
CI must verify that path. Checks are syntax/compilation only, not XML runtime
round trips; Python code is not imported during syntax checking.

At this stage UCI Rust and NeTEx failed the original budget. The larger-machine
follow-up below records the subsequent compiler fixes and deliberately chosen
UCI budget; initial failures are retained rather than relabeled as passes.

The follow-up `corpus-uci-rust-split` run explicitly enabled topological
chunking (25 emitted files versus 3 for the monolithic run). It also hit the
cgroup memory cap. Chunking is retained in the final harness, but this evidence
does not support claiming that splitting alone resolves Rust compilation.

## Larger-machine follow-up

UCI passes all seven targets in `corpus-uci-all-12000-final`, with codecs and
Serde enabled, Rust topological chunks, debug info disabled, and incremental
compilation disabled. The complete run uses a 12000 MiB cap and 600-second
per-command timeouts. The initial 11500 MiB Rust run exposed binary-field
type errors before cgroup OOM; binary fields now preserve XML lexical strings,
and the fixed Rust-only rerun passed at 11500 MiB. Scheduled UCI CI uses 12000
MiB to provide extra margin; other modules retain the 3500 MiB default.

NeTEx's original higher-budget run still exceeded 11500 MiB. Deduplicating
identical UPA source documents fixes exponential duplicate retention in shared
include graphs. The first deduplicated run used 2036360 KiB peak process RSS
at 3500 MiB and reached an imported-helper ownership error, not an OOM. After
that fix, Python compilation exposed a quoted-docstring syntax error, fixed
with an AST regression covering both Python backends. Subsequent results below
record the final outcomes. Intermediate cache-budget experiments were canceled
and removed from the implementation because they hurt shared-include reuse.

Final NeTEx outcomes in `corpus-netex-seven-final`: all seven source-generation
steps pass at 3500 MiB. Python compilation passes. Go fails on methods whose
receiver is an interface alias (`AbstractObject`); C++ has missing simple-union
type declarations (`NameOrNilReason` etc.); Java/C# contain duplicate nested
choice names; TypeScript has missing primitive aliases and interfaces extending
unions. Rust compilation exceeds the 3500 MiB cap. `--keep-going` records all
six failures and still exits nonzero.

The final complete compiler gate and W3C sample logs are retained alongside the
raw checks. The W3C sample matches the baseline: 31/31 schemas, 23/28 instances
with the same five pre-existing Python round-trip failures.

The complete validation/dry-run runner was also checked against the rebuilt
latest CLI (0.34.1 source on main) at 12000 MiB. It completes without OOM but
fails four validation suites: FHIR and AS4 resolve `xml:lang` as a type rather
than a global attribute; XBRL similarly fails on `xlink:type`; the W3C
meta-schema rejects its named `xs:openAttrs` type as an unknown built-in. The
full module graph stops at FHIR's same unresolved attribute. The full log is
`complete-validation-final.log`; these failures are not compilation passes.

## Remaining heavy modules on the rebuilt latest CLI

All generation steps pass at 3500 MiB; compiler failures remain nonzero and
retain complete logs. `hl7_cda`, `ubl_invoice`, and `finance_fpml` were checked
serially using the rebuilt compiler from 031ab53 (CLI version 0.34.1).

| Module | Python | Go | C++ | Java | TypeScript | C# | Rust |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hl7_cda | pass | fail | fail | pass | pass | fail | fail |
| ubl_invoice | pass | fail | fail | fail | fail | fail | fail |
| finance_fpml | pass | fail | fail | fail | fail | fail | fail |

CDA fails on Go declarations colliding with enum constants, missing C++ type
aliases, C# root/name collisions, and Rust codec conversions. UBL exposes
module import qualification/missing signature types, C++ alias/header collisions,
TypeScript primitive aliases, C# ambiguous imported names, and Rust codec issues.
FpML exposes duplicate choice branch names in Go/C++/Java/C#, TypeScript union
inheritance, and Rust missing lifetimes. NeTEx results above have the same
duplicate-choice and alias categories, plus the bounded Rust OOM. These are
follow-up generator bugs, not harness skips.

UCI passed all seven targets in the manual CI matrix at
https://github.com/polyxml/polyxml-schema-corpus/actions/runs/37109687233 .
Its raw artifact is retained in `corpus-uci-ci-success`. Rust took 173.076s
and peaked at 11978164 KiB process RSS under the 12000 MiB cap. The CI compiler
checkout was exactly 031ab535f122880d0afb6ae27abdef4ac5a4c999 (CLI 0.34.1;
subsequently released as 0.34.2). Corpus issues #1 and #3 are closed.
The remaining heavy jobs continue to collect their independent failures.
Ordinary PR/push CI passed both CDA/UBL Python checks and system-manager
harness regression tests. Full validation remains red; its failures and
heavy-module generator failures are tracked in PolyXML #134, #135, and #136.

## Full validation follow-up

PolyXML d3ecf31 parses imported inline global attributes and list item types,
accepts declared types in the schema-for-schemas namespace while still rejecting
unknown references, preserves owned ordered-content markers in module builds,
and assigns retained generated mixed-content helpers to a unique namespace
owner. C# optional enum attributes use a lexical XML proxy, with round-trip
regressions for present/absent values, namespaces, JSON naming, and invalid enums.

The corpus adds the shared `w3c_xml` owner/dependencies and rewrites the normative
meta-schema's XML import to its existing local mirror. **All 20 validation
suites and the 46-module graph now pass** at 12000 MiB, swap disabled, within
a ten-minute timeout. Raw verification logs are in `validation-followup/`.
The preceding validation failures are historical; generated-code compilation
failures in #135 remain separate and unresolved.
