# PolyXML Industry Schema Corpus & Benchmark Suite

[![PolyXML](https://img.shields.io/badge/PolyXML-Compiler-blue)](https://github.com/polyxml/PolyXML)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A curated collection of real-world, battle-tested enterprise XML Schema (XSD) suites used for stress testing, regression validation, and performance benchmarking of the [PolyXML](https://github.com/polyxml/PolyXML) multi-language code generation compiler.

---

## Why an Industry Schema Corpus?

Across open-source XSD generator trackers, certain widely adopted industry schemas are notorious for failing compilation or triggering out-of-memory errors. These real-world schemas stress every edge of XML Schema specifications:

- **Circular Type Graphs & Self-Referential Types**: Process definitions where nodes point to sequence flows that point back to nodes.
- **Deep Inheritance & Polymorphic Hierarchies**: Multi-level `xs:extension` inheritance trees (e.g. 6+ levels deep in BPMN 2.0).
- **Multi-Module Cross-Namespace Imports**: Shared cryptographic roots (e.g. W3C `xmldsig-core-schema.xsd`) imported into versioned profile namespaces across protocol versions.
- **Extreme Scale & Facet Density**: Thousands of types with heavy regex patterns, length restrictions, and same-named types across distinct domain namespaces.

This corpus ensures PolyXML reliably compiles and generates clean, idiomatic code across all **7 target languages** (Rust, TypeScript, Python, Go, C#, Java, and C++) without crashing or producing conflicting type declarations.

---

## Included Industry Suites

| Domain | Standard / Profile | Key Schemas | Complexity Characteristics |
| :--- | :--- | :--- | :--- |
| **Banking / SEPA** | ISO 20022 `camt.054.001.08` | `camt.054.001.08.xsd` | Bank-to-Customer Debit/Credit Notification. 265+ types, extreme facet restrictions, ISO currency/clearing codes, Gregorian partial date types. |
| **Banking / SEPA** | ISO 20022 `pacs.008.001.09` | `pacs.008.001.09.xsd` | Financial Institutional Customer Credit Transfer. 163+ types, dense inter-bank routing hierarchies. |
| **EV Charging** | ISO 15118 (V2G) | `V2G_CI_MsgDef.xsd`<br>`V2G_CI_MsgDataTypes.xsd`<br>`xmldsig-core-schema.xsd` | Electric Vehicle-to-Grid communication. Cross-namespace import with W3C XML Digital Signatures (`xmldsig`). Tests multi-schema deduplication (#81). |
| **BPM / Workflow** | OMG BPMN 2.0 | `BPMN20.xsd`<br>`Semantic.xsd`<br>`BPMNDI.xsd`<br>`DC.xsd`<br>`DI.xsd` | Business Process Model and Notation. Deep extension inheritance (`tBaseElement` &rarr; `tFlowElement` &rarr; `tFlowNode` &rarr; `tTask`), heavy `xs:substitutionGroup` usage. |
| **Healthcare** | HL7 CDA R2.1 | `CDA.xsd`<br>`POCD_MT000040UV02.xsd`<br>`NarrativeBlock.xsd` | Clinical Document Architecture. 1,450+ types, complex narrative mixed content, extensive clinical code vocabularies. |

---

## Directory Structure

```
polyxml-schema-corpus/
├── schemas/
│   ├── iso20022/              # SEPA & ISO 20022 financial messaging
│   │   ├── camt.054.001.08.xsd
│   │   └── pacs.008.001.09.xsd
│   ├── iso15118/              # ISO 15118 EV charging & W3C xmldsig
│   │   ├── V2G_CI_AppProtocol.xsd
│   │   ├── V2G_CI_MsgBody.xsd
│   │   ├── V2G_CI_MsgDataTypes.xsd
│   │   ├── V2G_CI_MsgDef.xsd
│   │   ├── V2G_CI_MsgHeader.xsd
│   │   └── xmldsig-core-schema.xsd
│   ├── bpmn20/                # OMG BPMN 2.0 process & diagram schemas
│   │   ├── BPMN20.xsd
│   │   ├── BPMNDI.xsd
│   │   ├── DC.xsd
│   │   ├── DI.xsd
│   │   └── Semantic.xsd
│   └── hl7-cda/               # HL7 Clinical Document Architecture R2.1
│       ├── CDA.xsd
│       ├── POCD_MT000040UV02.xsd
│       └── coreschemas/       # HL7 shared core datatypes & vocabulary
├── polyxml.toml               # Multi-module workspace configuration
├── runner.py                  # Automated validation and benchmark harness
├── LICENSE                    # Apache-2.0
└── README.md
```

---

## Usage

### 1. Run the Validation & Benchmark Suite

Ensure `polyxml` is installed or compiled in `../PolyXML/target/debug/polyxml`:

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
# Validate SEPA camt.054
polyxml validate schemas/iso20022/camt.054.001.08.xsd

# Validate ISO 15118 EV Charging suite
polyxml validate schemas/iso15118/*.xsd

# Validate BPMN 2.0 schemas
polyxml validate schemas/bpmn20/*.xsd
```

### 3. Build & Generate Code Across Modules

The root `polyxml.toml` defines modular boundaries with dependency resolution and type deduplication:

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
- **BPMN 2.0**: Object Management Group (OMG).
- **HL7 CDA**: Health Level Seven International.
- **XMLDSIG**: World Wide Web Consortium (W3C).

## License

This repository and its tooling scripts are licensed under the [Apache License, Version 2.0](LICENSE). Normative XSD schemas retain the notices and terms of their respective publishing bodies.
