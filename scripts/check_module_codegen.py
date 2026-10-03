#!/usr/bin/env python3
"""Generate a corpus module and its dependency closure, then compile serially."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = ("python", "go", "cpp", "java", "typescript", "csharp", "rust")
TOOLS = dict(
    zip(LANGUAGES, ("python3", "go", "g++", "javac", "tsc", "dotnet", "cargo"))
)


def closure(modules: dict, name: str) -> list[str]:
    result, visiting = [], set()

    def visit(key):
        if key in visiting:
            raise ValueError(f"cyclic module dependency: {key}")
        if key in result:
            return
        visiting.add(key)
        for dependency in modules[key].get("depends_on", []):
            visit(dependency)
        visiting.remove(key)
        result.append(key)

    visit(name)
    return result


def manifest(modules: dict, names: list[str], language: str) -> str:
    text = '[workspace]\nname = "corpus-check"\noutput_base_dir = "generated"\ngo_module = "polyxml/corpus-check"\n'
    for name in names:
        text += (
            f"\n[modules.{name}]\nschemas = {json.dumps(modules[name]['schemas'])}\n"
        )
        text += f"depends_on = {json.dumps(modules[name].get('depends_on', []))}\n"
    text += f'\n[[generate]]\ntarget = "{language}"\noutput = "{language}"\n'
    if language in ("java", "cpp"):
        text += (
            "package = "
            + json.dumps(
                "org.polyxml.corpus" if language == "java" else "polyxml::corpus"
            )
            + "\n"
        )
    return text


class BoundedRunner:
    def __init__(self, output: Path, memory: int, timeout: int, system: bool):
        self.output, self.memory, self.timeout = output, memory, timeout
        self.prefix = ["sudo", "-n"] if system else []
        self.manager = [] if system else ["--user"]
        self.identity = ["sudo", "-n", "-u", f"#{os.getuid()}", "--"] if system else []
        self.results = []

    def run(self, command: list[str], cwd: Path, label: str) -> None:
        unit = f"corpus-check-{uuid.uuid4().hex}.scope"
        log, stats = self.output / f"{label}.log", self.output / f"{label}.time"
        env = os.environ.copy()
        env.update(CARGO_BUILD_JOBS="1", GOMAXPROCS="1", LC_ALL="C")
        env.pop("CARGO_TARGET_DIR", None)
        bounded = self.prefix + [
            "systemd-run",
            *self.manager,
            "--scope",
            "--quiet",
            f"--unit={unit}",
            "-p",
            f"MemoryMax={self.memory}M",
            "-p",
            "MemorySwapMax=0",
            "--",
            *self.identity,
            "env",
            f"PATH={env['PATH']}",
            "CARGO_BUILD_JOBS=1",
            "GOMAXPROCS=1",
            "LC_ALL=C",
            "/usr/bin/time",
            "-v",
            "-o",
            str(stats),
            *command,
        ]
        start, code = time.monotonic(), 124
        print(f"{label}: {' '.join(command)}", flush=True)
        try:
            with log.open("w") as stream:
                proc = subprocess.Popen(
                    bounded, cwd=cwd, env=env, stdout=stream, stderr=subprocess.STDOUT
                )
                try:
                    code = proc.wait(timeout=self.timeout)
                except subprocess.TimeoutExpired:
                    stream.write(f"\nTIMEOUT after {self.timeout} seconds\n")
                finally:
                    try:
                        if code:
                            with (self.output / f"{label}.cgroup.log").open(
                                "w"
                            ) as diagnostics:
                                try:
                                    subprocess.run(
                                        self.prefix
                                        + [
                                            "journalctl",
                                            *self.manager,
                                            "-u",
                                            unit,
                                            "--no-pager",
                                            "-n",
                                            "30",
                                        ],
                                        stdout=diagnostics,
                                        stderr=subprocess.STDOUT,
                                        timeout=15,
                                        check=False,
                                    )
                                except subprocess.TimeoutExpired:
                                    diagnostics.write("journalctl timed out\n")
                    finally:
                        try:
                            subprocess.run(
                                self.prefix
                                + ["systemctl", *self.manager, "stop", unit],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                                timeout=15,
                                check=False,
                            )
                        finally:
                            if proc.poll() is None:
                                proc.kill()
                            proc.wait(timeout=15)
        finally:
            measurement = stats.read_text() if stats.exists() else ""
            rss = re.search(r"Maximum resident set size \(kbytes\): (\d+)", measurement)
            self.results.append(
                {
                    "label": label,
                    "command": command,
                    "exit_code": code,
                    "elapsed_seconds": round(time.monotonic() - start, 3),
                    "peak_rss_kib": int(rss[1]) if rss else None,
                    "memory_mib": self.memory,
                    "timeout_seconds": self.timeout,
                }
            )
            (self.output / "results.json").write_text(
                json.dumps(self.results, indent=2) + "\n"
            )
        if code:
            lines = log.read_text().splitlines()
            errors = [
                line
                for line in lines
                if re.search(r"error|fatal|killed|timeout", line, re.IGNORECASE)
            ]
            print("\n".join(errors[:10] or lines[-15:]), file=sys.stderr)
            raise RuntimeError(f"{label} failed ({code}); full log: {log}")


def compile_command(language: str, work: Path, core: Path) -> tuple[list[str], Path]:
    source = work / "generated" / language
    if language == "python":
        return ["python3", "-m", "compileall", "-q", str(source)], work
    if language == "go":
        return ["go", "test", "-p", "1", "./..."], source
    if language == "typescript":
        config = work / "tsconfig.json"
        config.write_text(
            json.dumps(
                {
                    "compilerOptions": {
                        "noEmit": True,
                        "skipLibCheck": True,
                        "target": "ES2020",
                    },
                    "include": ["generated/typescript/**/*.ts"],
                }
            )
        )
        return ["tsc", "-p", str(config)], work
    if language == "cpp":
        unit = work / "check.cpp"
        headers = sorted(source.glob("*/*.hpp"))
        if not headers:
            raise RuntimeError("no generated C++ headers")
        unit.write_text(
            "".join(f'#include "{path.relative_to(work)}"\n' for path in headers)
        )
        return [
            "g++",
            "-std=c++20",
            "-fsyntax-only",
            "-fmax-errors=10",
            str(unit),
        ], work
    if language == "java":
        files = sorted(source.rglob("*.java"))
        (work / "java-files.txt").write_text("".join(f'"{path}"\n' for path in files))
        return [
            "javac",
            "-J-Xmx2200m",
            "-Xmaxerrs",
            "10",
            "-d",
            str(work / "classes"),
            "@" + str(work / "java-files.txt"),
        ], work
    if language == "csharp":
        project = work / "Check.csproj"
        project.write_text(
            '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net8.0</TargetFramework><EnableDefaultCompileItems>false</EnableDefaultCompileItems></PropertyGroup><ItemGroup><Compile Include="generated/csharp/**/*.cs" /></ItemGroup></Project>'
        )
        return [
            "dotnet",
            "build",
            str(project),
            "--disable-build-servers",
            "-m:1",
            "-p:UseSharedCompilation=false",
        ], work
    (source / "Cargo.toml").write_text(
        '[package]\nname="corpus_check"\nversion="0.1.0"\nedition="2021"\n[workspace]\n[lib]\npath="mod.rs"\n[dependencies]\npolyxml={path='
        + json.dumps(str(core))
        + '}\nquick-xml={version="0.42",features=["serialize"]}\nserde={version="1",features=["derive"]}\nserde_json="1"\nregex="1"\n'
    )
    return ["cargo", "check", "--lib", "-j", "1"], source


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bin", type=Path, required=True)
    parser.add_argument(
        "--core", type=Path, default=ROOT.parent / "PolyXML" / "crates" / "polyxml-core"
    )
    parser.add_argument("-m", "--module", required=True)
    parser.add_argument("-l", "--lang", choices=LANGUAGES, action="append")
    parser.add_argument("--memory-mib", type=int, default=3500)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument(
        "--system",
        action="store_true",
        help="Use sudo system manager (CI); default uses user manager",
    )
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Local only: record missing toolchains as skips",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="New directory for retained logs and results",
    )
    args = parser.parse_args()
    modules = tomllib.loads((ROOT / "polyxml.toml").read_text())["modules"]
    if args.module not in modules or args.memory_mib <= 0 or args.timeout <= 0:
        parser.error("unknown module or nonpositive memory/timeout")
    compiler = args.bin.resolve(strict=True)
    core = args.core.resolve(strict=True)
    with compiler.open("rb") as binary:
        compiler_sha256 = hashlib.file_digest(binary, "sha256").hexdigest()
    selected = list(dict.fromkeys(args.lang or LANGUAGES))
    missing = [lang for lang in selected if not shutil.which(TOOLS[lang])]
    if missing and not args.allow_missing:
        parser.error(f"missing toolchains: {', '.join(missing)}")
    available = (
        int(re.search(r"MemAvailable:\s+(\d+)", Path("/proc/meminfo").read_text())[1])
        // 1024
    )
    if available < args.memory_mib + 1024:
        parser.error("memory cap must leave at least 1024 MiB available for the host")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    runner = BoundedRunner(output, args.memory_mib, args.timeout, args.system)
    try:
        # Fail closed if the selected manager cannot enforce a cgroup limit.
        runner.run(["/bin/true"], ROOT, "preflight")
        names = closure(modules, args.module)
        (output / "metadata.json").write_text(
            json.dumps(
                {
                    "module": args.module,
                    "closure": names,
                    "compiler": str(compiler),
                    "compiler_sha256": compiler_sha256,
                    "languages": selected,
                    "skipped": missing,
                    "check": "syntax/compile; no runtime round trips",
                },
                indent=2,
            )
            + "\n"
        )
        with tempfile.TemporaryDirectory(prefix="polyxml-corpus-check-") as directory:
            work = Path(directory)
            (work / "schemas").symlink_to(ROOT / "schemas", target_is_directory=True)
            for language in selected:
                if language in missing:
                    print(f"SKIP {language}: missing {TOOLS[language]}", flush=True)
                    continue
                config = manifest(modules, names, language)
                (work / "polyxml.toml").write_text(config)
                (output / f"{language}.toml").write_text(config)
                runner.run(
                    [str(compiler), "build", "--config", str(work / "polyxml.toml")],
                    work,
                    f"{language}-generate",
                )
                files = [
                    path
                    for path in (work / "generated" / language).rglob("*")
                    if path.is_file()
                ]
                if not files:
                    raise RuntimeError(f"{language}: no generated files")
                (output / f"{language}-files.json").write_text(
                    json.dumps(
                        {
                            "count": len(files),
                            "bytes": sum(path.stat().st_size for path in files),
                        },
                        indent=2,
                    )
                    + "\n"
                )
                command, cwd = compile_command(language, work, core)
                runner.run(command, cwd, f"{language}-compile")
    except (RuntimeError, subprocess.SubprocessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"All available selected targets passed. Logs: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
