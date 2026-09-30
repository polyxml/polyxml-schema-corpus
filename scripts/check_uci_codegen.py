#!/usr/bin/env python3
"""Generate and compile the UCI module one target at a time.

C++ is intentionally excluded until PolyXML can split large C++ compilation
units. Rust compilation units are automatically split into topological chunks.
This check keeps all output in a temporary directory.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = (
    "UCI_Versioning_v2_5_0.xsd",
    "UCI_SecurityMarkings_v2_5_0.xsd",
    "uci_entity_core.xsd",
    "UCI_MessageDefinitions_v2_5_0.xsd",
)
LANGUAGES = ("python", "go", "typescript", "java", "csharp", "rust")
OUTPUTS = {"python": "python", "go": "go", "typescript": "ts", "java": "java", "csharp": "csharp", "rust": "rs"}


def run(command: list[str], *, cwd: Path, timeout: int, memcap: Path, env_extra: dict[str, str] | None = None) -> None:
    command = [str(memcap), *command]
    print("$", " ".join(command), flush=True)
    env = os.environ.copy()
    env.setdefault("POLYXML_MEMCAP_PCT", "35")
    env.setdefault("GOMAXPROCS", "2")
    env.setdefault("CARGO_BUILD_JOBS", "2")
    env.setdefault("CARGO_TARGET_DIR", str(ROOT.parent / "PolyXML" / "target"))
    if env_extra:
        env.update(env_extra)
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError(
            f"command exited {result.returncode}: {' '.join(command)}\n"
            + "\n".join((result.stdout + result.stderr).splitlines()[:25])
        )
    for line in (result.stdout + result.stderr).splitlines()[-4:]:
        print(line)


def manifest(lang: str) -> str:
    schemas = ",\n    ".join(f'"schemas/defense-uci/{name}"' for name in SCHEMAS)
    package = 'package = "org.polyxml.uci"\n' if lang == "java" else ""
    return (
        '[workspace]\nname = "uci-compile-check"\noutput_base_dir = "generated"\n'
        'go_module = "polyxml/uci-check"\n\n'
        f'[modules.defense_uci]\nschemas = [\n    {schemas},\n]\n\n'
        f'[[generate]]\ntarget = "{lang}"\noutput = "{OUTPUTS[lang]}"\n{package}'
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bin", type=Path, required=True, help="PolyXML CLI executable")
    parser.add_argument("--lang", choices=LANGUAGES, action="append", help="Target to check; repeat to select several")
    parser.add_argument("--timeout", type=int, default=120, help="Seconds allowed for each command")
    args = parser.parse_args()
    compiler = args.bin.resolve(strict=True)
    selected = args.lang or LANGUAGES
    memcap = ROOT.parent / "PolyXML" / "scripts" / "memcap.sh"
    if not memcap.is_file():
        parser.error(f"memory cap wrapper not found: {memcap}")

    with tempfile.TemporaryDirectory(prefix="polyxml-uci-check-") as directory:
        work = Path(directory)
        (work / "schemas").symlink_to(ROOT / "schemas", target_is_directory=True)
        for lang in selected:
            print(f"\n== {lang} ==", flush=True)
            (work / "polyxml.toml").write_text(manifest(lang))
            run([str(compiler), "build", "--config", str(work / "polyxml.toml")], cwd=work, timeout=args.timeout, memcap=memcap)
            source = work / "generated" / OUTPUTS[lang] / "defense_uci"
            if lang == "python":
                command = ["python3", "-m", "py_compile", str(source / "defense_uci.py")]
                cwd = work
            elif lang == "go":
                command = ["go", "test", "./..."]
                cwd = work / "generated" / "go"
            elif lang == "typescript":
                command = ["tsc", "--noEmit", "--skipLibCheck", "--target", "ES2020", str(source / "defense_uci.ts")]
                cwd = work
            elif lang == "java":
                files = sorted(str(path) for path in source.glob("*.java"))
                assert files, "no generated Java files"
                (work / "java-files.txt").write_text("\n".join(files) + "\n")
                classes = work / "java-classes"
                classes.mkdir(exist_ok=True)
                command = ["javac", "-J-Xmx1500m", "-Xmaxerrs", "10", "-d", str(classes), f"@{work / 'java-files.txt'}"]
                cwd = work
            elif lang == "csharp":
                project = work / "UciCheck.csproj"
                project.write_text(
                    '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net8.0</TargetFramework>'
                    '<EnableDefaultCompileItems>false</EnableDefaultCompileItems></PropertyGroup>'
                    '<ItemGroup><Compile Include="generated/csharp/defense_uci/*.cs" /></ItemGroup></Project>\n'
                )
                command = ["dotnet", "build", str(project), "--ignore-failed-sources", "-p:UseSharedCompilation=false"]
                cwd = work
            elif lang == "rust":
                polyxml_core = ROOT.parent / "PolyXML" / "crates" / "polyxml-core"
                target_dir = ROOT.parent / "PolyXML" / "target"
                cargo_toml = work / "generated" / "rs" / "Cargo.toml"
                cargo_toml.write_text(
                    f'[package]\nname = "uci_check"\nversion = "0.1.0"\nedition = "2021"\n\n'
                    f'[lib]\npath = "defense_uci/mod.rs"\n\n'
                    f'[dependencies]\n'
                    f'polyxml = {{ path = "{polyxml_core}" }}\n'
                    f'quick-xml = {{ version = "0.42", features = ["serialize"] }}\n'
                    f'serde = {{ version = "1.0", features = ["derive"] }}\n'
                    f'serde_json = "1.0"\n'
                    f'regex = "1.11"\n'
                )
                command = ["cargo", "check", "--lib", "-j", "2", "--target-dir", str(target_dir)]
                cwd = work / "generated" / "rs"
            else:
                raise ValueError(f"Unsupported target: {lang}")
            env_extra = {"POLYXML_MEMCAP_PCT": "50"} if lang == "rust" else None
            run(command, cwd=cwd, timeout=args.timeout, memcap=memcap, env_extra=env_extra)
    print("\nAll selected UCI targets compiled.")


if __name__ == "__main__":
    main()
