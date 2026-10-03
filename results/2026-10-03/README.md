# Bounded corpus checks — 2026-10-03

Latest: UCI passes all seven targets locally at 12000 MiB using the compiler
fixes published in PolyXML 031ab53. NeTEx Python passes at 3500 MiB after UPA
source deduplication, module ownership, and quoted-docstring fixes. These checks
verify compilation, not runtime XML conformance. Detailed outcomes and historical
failures follow.

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
