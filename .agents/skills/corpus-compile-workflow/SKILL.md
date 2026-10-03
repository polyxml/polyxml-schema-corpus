---
name: corpus-compile-workflow
description: Generate corpus module dependency closures and verify all seven destination languages under fixed systemd cgroup limits.
---

Use scripts/check_module_codegen.py with -m MODULE, optional repeated -l LANGUAGE,
--bin PATH, and a new --output directory. Defaults: 3500 MiB, swap disabled,
600 seconds per command, serial compilation. Never bypass the cap after failure.
Local runs require a working user systemd manager; CI uses --system and sudo.
CI checks out PolyXML inside the corpus, so pass --core PolyXML/crates/polyxml-core.
Otherwise the default is the sibling PolyXML checkout. The selected module and
all dependencies are read from polyxml.toml; compile the full generated closure.

Run python3 -m unittest discover -s tests -v to verify limits, error retention,
and descendant cleanup on timeout. User-manager tests skip when unavailable;
CI's real generation/compilation jobs enforce the system-manager path.
Retain logs, results.json, metadata.json, and file counts when publishing evidence.
Record exact compiler source commit and tool versions with local results.
Do not treat syntax compilation as runtime XML conformance or skipped targets
as full success. C# net8.0 build tests need the SDK/reference pack but no runtime
execution. Missing toolchains are fatal unless --allow-missing is explicit.

Rust chunking is opt-in (`split_units = true`, `chunk_size = 250` in the
generated manifest), not automatic. Inspect emitted file counts and preserve
this setting in regression tests; a monolithic run does not test the split
strategy. Both strategies still share one cargo check crate.

UCI's complete Rust codec/Serde check needs ~11.2 GiB process RSS. Use the
12000 MiB documented CI/local budget with at least 1 GiB additional available
headroom. Other heavy modules retain the 3500 MiB default. Rust compile checks
disable debug info and incremental compilation; they keep codecs and Serde.
Use --keep-going to collect every target outcome serially; any target failure
still produces a nonzero final exit and a retained failures.json. Scheduled
CI uses this mode. Never label failed targets as skipped or passing.

Keep workflow concurrency groups separate by event name so routine main pushes
do not cancel a weekly/manual heavy matrix partway through its serial checks.

The corpus has 46 modules, including a shared w3c_xml owner for anonymous
XML-namespace attribute types. XHTML/FHIR, schema-for-schemas, SOAP/AS4, and
Dublin Core/railML closures include it through declared dependencies. Keep the
W3C meta-schema XML import pointed at its existing sibling xml.xsd mirror;
compiler imports do not fetch HTTP schemas implicitly. Verify the full runner
after changing schema ownership as well as selected generated-code closures.
