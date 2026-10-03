<h1 align="center">
  <img src="https://raw.githubusercontent.com/polyxml/PolyXML/main/docs/assets/brand/logo_polyxml_banner.png" alt="PolyXML" width="1000">
</h1>

<p align="center">
  <strong>PolyXML Industry Schema Corpus & Multi-Language Benchmark Suite</strong><br>
  <em>20 Battle-Tested Enterprise Standards • 45 Modules • 6,800+ Owned Types</em>
</p>

<p align="center">
  <a href="https://github.com/polyxml/PolyXML"><img src="https://img.shields.io/badge/PolyXML-Compiler-blue.svg?logo=rust" alt="PolyXML Compiler"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT"></a>
  <a href="NOTICE"><img src="https://img.shields.io/badge/Attribution-NOTICE-blue.svg" alt="Attribution: NOTICE"></a>
  <a href="https://github.com/polyxml/PolyXML/actions"><img src="https://img.shields.io/github/actions/workflow/status/polyxml/PolyXML/ci.yml?branch=main&label=CI&logo=github" alt="CI"></a>
  <a href="#included-industry-suites"><img src="https://img.shields.io/badge/Standards-20%20Suites-orange.svg" alt="20 Standards"></a>
  <a href="#included-industry-suites"><img src="https://img.shields.io/badge/Types-6%2C800%2B-blueviolet.svg" alt="6,800+ Types"></a>
</p>

---

A curated collection of real-world, battle-tested enterprise XML Schema (XSD) suites spanning banking, healthcare, transit, aviation, capital markets, defense, geospatial, and regulatory domains. Used for stress testing, regression validation, and performance benchmarking of the **[PolyXML](https://github.com/polyxml/PolyXML)** multi-language code generation compiler.

---

## 🏛️ Why an Industry Schema Corpus?

Across open-source XSD generator trackers, certain widely adopted industry schemas are notorious for failing compilation, hanging in infinite loops, or triggering out-of-memory errors. These real-world enterprise schemas stress every corner of the W3C XML Schema 1.0 and 1.1 specifications:

- **Circular Type Graphs & Self-Referential Types**: Flight trajectories, process graphs, and linked asset events (handled via Tarjan Strongly Connected Component detection).
- **Deep Inheritance & Polymorphic Hierarchies**: Multi-level `xs:extension` inheritance trees (e.g. 6+ levels deep in BPMN 2.0 and NeTEx).
- **Multi-Module Cross-Namespace Imports**: Shared cryptographic and metadata roots (e.g. W3C `xmldsig`, `xmlenc`, `xlink`, `xAL`) imported across protocol versions.
- **Extreme Scale & Facet Density**: Massive industrial standards with thousands of types (e.g. NeTEx with 2,400+ types, HL7 CDA with 1,450+ types, UBL with 1,000+ types).
- **Multi-Megabyte Monolithic Schemas**: Massive schema files such as NATO UCI (8.0 MB single file) and HL7 FHIR (2.6 MB).

The default validation run checks schema parsing and module ownership. A separate
parameterized check generates source and compiles seven destination languages
serially under a hard cgroup memory limit. Scheduled/manual CI checks UCI, CDA,
UBL Invoice, NeTEx, and FpML; ordinary PR CI checks CDA and UBL Python syntax.

---

## 📦 Included Industry Suites

| Domain | Standard / Organization | Key Schemas | Complexity Characteristics |
| :--- | :--- | :--- | :--- |
| **Banking / Payments** | ISO 20022 `camt.054.001.08` | `camt.054.001.08.xsd` | Bank-to-Customer Debit/Credit Notification. 265+ types, extreme facet restrictions, ISO currency/clearing codes, partial date types. |
| **Banking / Payments** | ISO 20022 `pacs.008.001.09` | `pacs.008.001.09.xsd` | Financial Institutional Customer Credit Transfer. 163+ types, dense inter-bank routing hierarchies. |
| **Banking / SEPA** | ISO 20022 `pain.001.001.10` | `pain.001.001.10.xsd` | Customer Credit Transfer Initiation (SEPA payments). 167+ types, cash management structures. |
| **Procurement / Invoicing** | OASIS UBL 2.1 | `UBL-Invoice-2.1.xsd`<br>`UBL-Order-2.1.xsd` | Universal Business Language (PEPPOL e-invoicing). 1,000+ types, 1,600+ elements, CCTS core component types, ETSI XAdES signatures. |
| **Derivatives / Capital Markets** | ISDA FpML 5.12 | `fpml-main-5-12.xsd`<br>`fpml-ird-5-12.xsd` | Financial products Markup Language for OTC derivatives, interest rate swaps, equity options, and credit default swaps. 250+ types, 24 circular cut points. |
| **Financial Reporting** | XBRL 2.1 | `xbrl-instance-2003-12-31.xsd`<br>`xbrl-linkbase-2003-12-31.xsd` | Extensible Business Reporting Language for SEC and ESMA statutory filings. Multi-file XLink relationships, recursive arcs. |
| **Healthcare** | HL7 CDA R2.1 | `CDA.xsd`<br>`POCD_MT000040UV02.xsd` | Clinical Document Architecture. 1,450+ types, complex narrative mixed content, extensive clinical code vocabularies. |
| **Healthcare** | HL7 FHIR R4 | `fhir-single.xsd`<br>`fhir-xhtml.xsd` | Fast Healthcare Interoperability Resources. 169+ types, 53 root resources, embedded W3C XHTML narrative blocks. |
| **EV Charging / Smart Grid** | ISO 15118 (V2G) | `V2G_CI_MsgDef.xsd`<br>`xmldsig-core-schema.xsd` | Electric Vehicle-to-Grid communication. Cross-namespace import with W3C XML Digital Signatures (`xmldsig`). Tests multi-schema deduplication (#81). |
| **Aviation / Air Traffic** | ICAO & FAA FIXM 4.0 | `Fixm.xsd`<br>`Nas.xsd`<br>`Flight.xsd` | Flight Information Exchange Model for NextGen air traffic management. 120+ types, 48 circular flight trajectory cut points. |
| **Transit / Timetables** | CEN NeTEx (CEN/TS 16614) | `NeTEx_publication_timetable.xsd` | European standard for public transport static data, timetables, and stop topology. Colossal scale: **2,400+ types, 720+ root elements**. |
| **Transit / Telemetry** | CEN SIRI (CEN/TS 15531) | `siri_all_framework-v2.0.xsd` | Service Interface for Real Time Information across European public transport operators. |
| **Transit / Rail** | railML 2.4 | `railML.xsd`<br>`infrastructure.xsd` | Railway Markup Language for rail network infrastructure, rolling stock, and interlocking timetables. |
| **Defense / Autonomous Systems** | US DoD / NATO UCI v2.5 | `UCI_MessageDefinitions_v2_5_0.xsd` | Universal Command and Control Interface for autonomous and unmanned aerial systems. **8.0 MB** monolithic schema. |
| **BPM / Workflow** | OMG BPMN 2.0 | `BPMN20.xsd`<br>`Semantic.xsd` | Business Process Model and Notation. Deep extension inheritance (`tBaseElement` &rarr; `tFlowElement` &rarr; `tFlowNode` &rarr; `tTask`), heavy `xs:substitutionGroup` usage. |
| **Geospatial / GIS** | OGC KML 2.2 | `ogckml22.xsd`<br>`atom-author-link.xsd` | Open Geospatial Consortium Keyhole Markup Language (Google Earth, GIS features). 216+ types, 276 elements, OASIS CIQ address integration. |
| **Geospatial / GIS** | OGC GML 3.2.1 (ISO 19136) | `gml_extract_all_objects_v_3_2_1.xsd` | Geography Markup Language foundation for geographic coordinate systems, topologies, and feature geometries. |
| **Identity / Security** | OASIS SAML 2.0 | `saml-schema-protocol-2.0.xsd`<br>`saml-schema-assertion-2.0.xsd` | Security Assertion Markup Language for enterprise single sign-on (SSO), federation, and token exchange. Integrates W3C `xmlenc` and `xmldsig`. |
| **B2B Messaging** | OASIS ebMS 3.0 / AS4 | `ebms-header-3_0.xsd`<br>`soap-envelope-1.2.xsd` | Secure B2B message packaging used by Peppol, e-Codex, and energy grids. SOAP 1.1/1.2 envelope integration. |
| **Meta-Schema** | W3C XML Schema | `XMLSchema.xsd`<br>`xml.xsd` | The normative self-referential W3C schema for XML Schema itself. Validates recursive schema definition parsing. |

---

## 📁 Directory Structure

```
polyxml-schema-corpus/
├── schemas/
│   ├── aviation-fixm/         # FAA / Eurocontrol / ICAO FIXM 4.0
│   ├── bpmn20/                # OMG BPMN 2.0 process & diagram schemas
│   ├── defense-uci/           # US DoD / NATO UCI v2.5 (8.0 MB schema)
│   ├── finance-fpml/          # ISDA FpML 5.12 OTC derivatives & swaps
│   ├── geospatial-kml/        # OGC KML 2.2 GIS & Earth models
│   ├── hl7-cda/               # HL7 Clinical Document Architecture R2.1
│   ├── hl7-fhir/              # HL7 FHIR R4 healthcare resources & XHTML
│   ├── iso15118/              # ISO 15118 EV charging & W3C xmldsig
│   ├── iso20022/              # SEPA & ISO 20022 (camt.054, pacs.008, pain.001)
│   ├── messaging-as4/         # OASIS ebMS 3.0 / AS4 & SOAP envelopes
│   ├── regulatory-xbrl/       # XBRL 2.1 financial filings & XLink
│   ├── security-saml/         # OASIS SAML 2.0 assertions & protocols
│   ├── transit-netex/         # CEN NeTEx timetables & OGC GML 3.2.1
│   ├── transit-railml/        # railML 2.4 railway transport schemas
│   ├── transit-siri/          # CEN SIRI real-time transit telemetry
│   ├── ubl-2.1/               # OASIS UBL 2.1 procurement & invoicing
│   └── w3c-xmlschema/         # Normative W3C XML Schema definition
├── polyxml.toml               # Multi-module workspace configuration (45 modules)
├── runner.py                  # Automated validation and benchmark harness
├── scripts/check_module_codegen.py # Parameterized bounded compile check
├── scripts/check_uci_codegen.py # UCI compatibility entry point
├── LICENSE                    # MIT License
├── NOTICE                     # Standards attribution & third-party copyright notices
└── README.md
```

---

## ⚡ Usage

### Bounded generated-code compilation

Install Python 3.12+, Go, g++ (C++20), Java 25, TypeScript 5 (`tsc`),
.NET 8 SDK, and Rust. Linux with cgroup v2 and a working systemd user manager
is required locally; CI uses the system manager through passwordless sudo.

```bash
python3 scripts/check_module_codegen.py --bin ../PolyXML/target/debug/polyxml \
  -m defense_uci --memory-mib 12000 --output /tmp/uci-compile-results
python3 scripts/check_module_codegen.py --bin ../PolyXML/target/debug/polyxml \
  -m ubl_invoice -l python --output /tmp/ubl-python-results
```

The harness reads the selected module and its transitive dependencies from
`polyxml.toml`, emits actual source, and checks one language at a time.
Repeat `-l` / `--lang` to select targets; the default is all seven.
`check_uci_codegen.py` remains a compatibility entry point selecting `defense_uci`
and accepts the same options (including required `--output`).

Every generation and compile command runs in a separate systemd scope with
`MemoryMax=3500M` by default and `MemorySwapMax=0`. UCI Rust needs the larger
12,000 MiB budget used by its scheduled/manual CI job; local full-UCI runs
should pass `--memory-mib 12000` with sufficient headroom. The ten-minute timeout stops the entire
scope, including compiler children. The cap must leave at least 1 GiB available
for the host; no uncapped fallback is permitted. `--memory-mib` and `--timeout`
allow deliberate budget changes. Rust checks explicitly enable `split_units = true` with 250-type chunks;
chunking is opt-in in PolyXML. Rust checks disable debug info and incremental
compilation to avoid unnecessary compiler memory overhead. Rust/Go builds use one worker; Java's heap
is additionally limited to 2200 MiB. `--system` selects CI's system manager
and runs compilers as the invoking user. Missing tools fail before generation;
`--allow-missing` is for local partial runs only and records explicit skips.

The output directory must be new. It retains manifests, generated file counts
and bytes, full command logs, GNU time resource reports (peak process RSS),
and machine-readable elapsed times/exit statuses. Generated source and build
products are temporary. RSS is a process measurement, not total cgroup memory;
the kernel cap covers the whole tree. These are syntax/compile checks, not XML
runtime round trips. Any failure or timeout returns nonzero; a failed target
stops that module run and remains visible in CI artifacts by default.
`--keep-going` checks the remaining targets while retaining a nonzero final exit
status; scheduled/manual CI uses it to collect all seven outcomes.

PR/push CI checks `hl7_cda` and `ubl_invoice` Python. Weekly and manual CI
runs all seven languages for `defense_uci`, `hl7_cda`, `ubl_invoice`,
`transit_netex`, and `finance_fpml`, with heavy matrix jobs serialized.
The original validation/dry-run job remains separate.

Published [2026-10-03 results](results/2026-10-03/README.md) show UCI passing
all seven targets locally and in GitHub CI at 12000 MiB. Other heavy modules have remaining
[compiler failures](https://github.com/polyxml/PolyXML/issues/135); full-corpus
validation also exposes [inline global attribute support](https://github.com/polyxml/PolyXML/issues/134)
and [schema-for-schemas validation](https://github.com/polyxml/PolyXML/issues/136).
The scheduled matrix retains these failures in its artifacts.

Harness regression tests (including real user-cgroup limit and timeout checks):

```bash
python3 -m unittest discover -s tests -v
```

### 1. Run the Validation & Benchmark Suite

Ensure `polyxml` is installed or compiled in `../PolyXML/target/release/polyxml`:

```bash
python3 runner.py
```

To test against an explicit `polyxml` binary:

```bash
python3 runner.py --bin /path/to/polyxml
```

### 2. Validate Individual Schemas

You can validate any individual schema or directory directly via the PolyXML CLI:

```bash
# Validate SEPA Credit Transfer (pain.001)
polyxml validate schemas/iso20022/pain.001.001.10.xsd

# Validate OASIS UBL 2.1 Invoice
polyxml validate schemas/ubl-2.1/maindoc/UBL-Invoice-2.1.xsd

# Validate CEN NeTEx publication timetable (2,400+ types)
polyxml validate schemas/transit-netex/NeTEx_publication_timetable.xsd

# Validate NATO UCI Message Definitions (8.0 MB)
polyxml validate schemas/defense-uci/UCI_MessageDefinitions_v2_5_0.xsd
```

### 3. Build & Generate Code Across Modules

The root `polyxml.toml` defines modular boundaries with dependency resolution and type deduplication across all 45 modules:

```bash
# Test schema resolution & module graph in dry-run mode
polyxml build --dry-run

# Generate code for all 7 languages into ./generated/
polyxml build
```

---

## ⚖️ Standards Attribution & License

- **Repository Tooling & Automation**: Licensed under the [MIT License](LICENSE).
- **Normative XML Schemas**: Authored by respective international standards bodies (ISO, OASIS, W3C, OMG, HL7, ISDA, XBRL, ICAO/FAA, CEN, railML.org, OGC). Retain all copyright notices, warranties, and terms of use stipulated by their publishing bodies. See [NOTICE](NOTICE) for full attribution details.
