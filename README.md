# PolyXML Industry Schema Corpus & Benchmark Suite

[![PolyXML](https://img.shields.io/badge/PolyXML-Compiler-blue)](https://github.com/polyxml/PolyXML)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A curated collection of real-world, battle-tested enterprise XML Schema (XSD) suites spanning banking, healthcare, transit, aviation, capital markets, defense, geospatial, and regulatory domains. Used for stress testing, regression validation, and performance benchmarking of the [PolyXML](https://github.com/polyxml/PolyXML) multi-language code generation compiler.

---

## Why an Industry Schema Corpus?

Across open-source XSD generator trackers, certain widely adopted industry schemas are notorious for failing compilation, hanging in infinite loops, or triggering out-of-memory errors. These real-world enterprise schemas stress every corner of the W3C XML Schema 1.0/1.1 specifications:

- **Circular Type Graphs & Self-Referential Types**: Flight trajectories, process graphs, and linked asset events (handled via Tarjan Strongly Connected Component detection).
- **Deep Inheritance & Polymorphic Hierarchies**: Multi-level `xs:extension` inheritance trees (e.g. 6+ levels deep in BPMN 2.0 and NeTEx).
- **Multi-Module Cross-Namespace Imports**: Shared cryptographic and metadata roots (e.g. W3C `xmldsig`, `xmlenc`, `xlink`, `xAL`) imported across protocol versions.
- **Extreme Scale & Facet Density**: Massive industrial standards with thousands of types (e.g. NeTEx with 2,400+ types, HL7 CDA with 1,450+ types, UBL with 1,000+ types).
- **Multi-Megabyte Monolithic Schemas**: Schemas such as NATO UCI (8.0 MB single file) and HL7 FHIR (2.6 MB).

This corpus ensures PolyXML reliably compiles and generates clean, idiomatic code across all **7 target languages** (Rust, TypeScript, Python, Go, C#, Java, and C++) without crashing or producing conflicting type declarations.

---

## Included Industry Suites

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
| **Defense / Unmanned Systems** | US DoD / NATO UCI v2.5 | `UCI_MessageDefinitions_v2_5_0.xsd` | Universal Command and Control Interface for autonomous and unmanned aerial systems. **8.0 MB** monolithic schema. |
| **BPM / Workflow** | OMG BPMN 2.0 | `BPMN20.xsd`<br>`Semantic.xsd` | Business Process Model and Notation. Deep extension inheritance (`tBaseElement` &rarr; `tFlowElement` &rarr; `tFlowNode` &rarr; `tTask`), heavy `xs:substitutionGroup` usage. |
| **Geospatial / GIS** | OGC KML 2.2 | `ogckml22.xsd`<br>`atom-author-link.xsd` | Open Geospatial Consortium Keyhole Markup Language (Google Earth, GIS features). 216+ types, 276 elements, OASIS CIQ address integration. |
| **Geospatial / GIS** | OGC GML 3.2.1 (ISO 19136) | `gml_extract_all_objects_v_3_2_1.xsd` | Geography Markup Language foundation for geographic coordinate systems, topologies, and feature geometries. |
| **Identity / Security** | OASIS SAML 2.0 | `saml-schema-protocol-2.0.xsd`<br>`saml-schema-assertion-2.0.xsd` | Security Assertion Markup Language for enterprise single sign-on (SSO), federation, and token exchange. Integrates W3C `xmlenc` and `xmldsig`. |
| **B2B Messaging** | OASIS ebMS 3.0 / AS4 | `ebms-header-3_0.xsd`<br>`soap-envelope-1.2.xsd` | Secure B2B message packaging used by Peppol, e-Codex, and energy grids. SOAP 1.1/1.2 envelope integration. |
| **Meta-Schema** | W3C XML Schema | `XMLSchema.xsd`<br>`xml.xsd` | The normative self-referential W3C schema for XML Schema itself. Validates recursive schema definition parsing. |

---

## Directory Structure

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
├── LICENSE                    # Apache-2.0
└── README.md
```

---

## Usage

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

## Standards & Attribution

The XML schemas included in this corpus are normative specifications published by international standards bodies:
- **ISO 20022**: International Organization for Standardization / European Payments Council.
- **ISO 15118**: International Organization for Standardization / CharIN.
- **OASIS**: Universal Business Language (UBL), SAML, ebMS/AS4, CIQ.
- **OMG**: Object Management Group (BPMN 2.0).
- **HL7**: Health Level Seven International (CDA, FHIR).
- **ISDA**: International Swaps and Derivatives Association (FpML).
- **XBRL**: XBRL International.
- **ICAO / FAA / Eurocontrol**: Flight Information Exchange Model (FIXM).
- **CEN**: European Committee for Standardization (NeTEx, SIRI).
- **railML.org**: Railway Markup Language initiative.
- **OGC**: Open Geospatial Consortium (GML, KML).
- **W3C**: World Wide Web Consortium (XML Schema, XMLDSIG, XMLEnc, XLink, XHTML).

## License

This repository and its tooling scripts are licensed under the [Apache License, Version 2.0](LICENSE). Normative XSD schemas retain the notices and terms of their respective publishing bodies.
