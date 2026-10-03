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
