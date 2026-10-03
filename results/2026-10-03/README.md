# Bounded corpus checks — 2026-10-03

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

UCI's seven-language gate is not green: corpus issue #1 must remain open until
Rust compilation succeeds within the chosen budget. NeTEx likewise needs
memory work before its scheduled check can pass. The harness intentionally
reports these failures instead of treating them as skips or increasing caps.

The follow-up `corpus-uci-rust-split` run explicitly enabled topological
chunking (25 emitted files versus 3 for the monolithic run). It also hit the
cgroup memory cap. Chunking is retained in the final harness, but this evidence
does not support claiming that splitting alone resolves Rust compilation.
