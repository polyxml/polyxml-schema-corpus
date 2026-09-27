#!/usr/bin/env python3
"""PolyXML Industry Schema Corpus & Benchmark Runner

Automates validation, codegen, and compilation benchmarking across 20
notorious real-world enterprise XML schemas (ISO 20022 SEPA, OASIS UBL,
HL7 FHIR, HL7 CDA, ISO 15118 EV Charging, BPMN 2.0, ISDA FpML, CEN NeTEx,
ICAO/FAA FIXM, NATO UCI, XBRL, SAML 2.0, railML, etc.).
Licensed under MIT.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent

SCHEMAS = {
    "SEPA camt.054 (ISO 20022)": [
        "schemas/iso20022/camt.054.001.08.xsd",
    ],
    "SEPA pacs.008 (ISO 20022)": [
        "schemas/iso20022/pacs.008.001.09.xsd",
    ],
    "SEPA pain.001 (ISO 20022)": [
        "schemas/iso20022/pain.001.001.10.xsd",
    ],
    "ISO 15118 EV Charging": [
        "schemas/iso15118/xmldsig-core-schema.xsd",
        "schemas/iso15118/V2G_CI_AppProtocol.xsd",
        "schemas/iso15118/V2G_CI_MsgDataTypes.xsd",
        "schemas/iso15118/V2G_CI_MsgHeader.xsd",
        "schemas/iso15118/V2G_CI_MsgBody.xsd",
        "schemas/iso15118/V2G_CI_MsgDef.xsd",
    ],
    "BPMN 2.0 (OMG)": [
        "schemas/bpmn20/DC.xsd",
        "schemas/bpmn20/DI.xsd",
        "schemas/bpmn20/BPMNDI.xsd",
        "schemas/bpmn20/Semantic.xsd",
        "schemas/bpmn20/BPMN20.xsd",
    ],
    "HL7 CDA R2.1": [
        "schemas/hl7-cda/coreschemas/voc.xsd",
        "schemas/hl7-cda/coreschemas/datatypes-base.xsd",
        "schemas/hl7-cda/coreschemas/datatypes.xsd",
        "schemas/hl7-cda/coreschemas/infrastructureRoot.xsd",
        "schemas/hl7-cda/coreschemas/NarrativeBlock.xsd",
        "schemas/hl7-cda/POCD_MT000040UV02.xsd",
        "schemas/hl7-cda/CDA.xsd",
    ],
    "HL7 FHIR R4": [
        "schemas/hl7-fhir/fhir-xhtml.xsd",
        "schemas/hl7-fhir/fhir-single.xsd",
    ],
    "OASIS UBL 2.1": [
        "schemas/ubl-2.1/maindoc/UBL-Invoice-2.1.xsd",
        "schemas/ubl-2.1/maindoc/UBL-Order-2.1.xsd",
    ],
    "W3C XML Schema": [
        "schemas/w3c-xmlschema/XMLSchema.xsd",
    ],
    "OASIS SAML 2.0": [
        "schemas/security-saml/saml-schema-assertion-2.0.xsd",
        "schemas/security-saml/saml-schema-protocol-2.0.xsd",
    ],
    "XBRL 2.1 Financial Filings": [
        "schemas/regulatory-xbrl/xbrl-instance-2003-12-31.xsd",
    ],
    "OGC KML 2.2": [
        "schemas/geospatial-kml/ogckml22.xsd",
    ],
    "OGC GML 3.2.1 (ISO 19136)": [
        "schemas/transit-netex/gml/gml_extract_all_objects_v_3_2_1.xsd",
    ],
    "FIXM 4.0 (ICAO & FAA Aviation)": [
        "schemas/aviation-fixm/core/base/Base.xsd",
        "schemas/aviation-fixm/core/flight/Flight.xsd",
        "schemas/aviation-fixm/core/messaging/Messaging.xsd",
        "schemas/aviation-fixm/core/Fixm.xsd",
        "schemas/aviation-fixm/extensions/nas/Nas.xsd",
    ],
    "FpML 5.12 (ISDA Derivatives)": [
        "schemas/finance-fpml/fpml-main-5-12.xsd",
    ],
    "Transit SIRI (CEN)": [
        "schemas/transit-siri/siri/siri_all_framework-v2.0.xsd",
    ],
    "Transit NeTEx (CEN Timetables)": [
        "schemas/transit-netex/NeTEx_publication_timetable.xsd",
    ],
    "Transit RailML 2.4": [
        "schemas/transit-railml/railML.xsd",
    ],
    "OASIS ebMS 3.0 / AS4": [
        "schemas/messaging-as4/ebms-header-3_0.xsd",
    ],
    "Defense UCI (US DoD / NATO)": [
        "schemas/defense-uci/UCI_Versioning_v2_5_0.xsd",
        "schemas/defense-uci/UCI_SecurityMarkings_v2_5_0.xsd",
        "schemas/defense-uci/uci_entity_core.xsd",
        "schemas/defense-uci/UCI_MessageDefinitions_v2_5_0.xsd",
    ],
}


def find_polyxml() -> str:
    """Locate polyxml executable from local development build or PATH."""
    dev_release = ROOT.parent / "PolyXML" / "target" / "release" / "polyxml"
    if dev_release.exists():
        return str(dev_release)

    dev_debug = ROOT.parent / "PolyXML" / "target" / "debug" / "polyxml"
    if dev_debug.exists():
        return str(dev_debug)

    which = shutil.which("polyxml")
    if which:
        return which

    sys.exit("Error: 'polyxml' binary not found. Install it or build PolyXML in ../PolyXML.")


def run_validate(polyxml: str) -> bool:
    print("\n" + "=" * 60)
    print("STEP 1: Validating schemas with polyxml validate")
    print("=" * 60)
    all_ok = True
    for suite, files in SCHEMAS.items():
        print(f"\n[Suite] {suite} ({len(files)} files)")
        cmd = [polyxml, "validate"] + [str(ROOT / f) for f in files]
        start = time.perf_counter()
        proc = subprocess.run(cmd, capture_output=True, text=True)
        elapsed = (time.perf_counter() - start) * 1000
        if proc.returncode == 0:
            print(f"  ✓ Validated in {elapsed:.2f}ms")
        else:
            print(f"  ✗ FAILED ({elapsed:.2f}ms):\n{proc.stderr}")
            all_ok = False
    return all_ok


def run_dry_run(polyxml: str) -> bool:
    print("\n" + "=" * 60)
    print("STEP 2: Workspace dry-run compilation (polyxml.toml)")
    print("=" * 60)
    cmd = [polyxml, "build", "--dry-run", "--config", str(ROOT / "polyxml.toml")]
    start = time.perf_counter()
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    elapsed = (time.perf_counter() - start) * 1000
    if proc.returncode == 0:
        print(proc.stdout.strip())
        print(f"\n✓ All modules parsed and ownership verified in {elapsed:.2f}ms")
        return True
    else:
        print(f"✗ Build dry-run failed:\n{proc.stderr}")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="PolyXML Industry Schema Corpus Runner")
    parser.add_argument("--bin", help="Explicit path to polyxml binary")
    args = parser.parse_args()

    polyxml = args.bin or find_polyxml()
    print(f"Using PolyXML binary: {polyxml}")

    val_ok = run_validate(polyxml)
    build_ok = run_dry_run(polyxml)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Validation: {'PASSED' if val_ok else 'FAILED'}")
    print(f"Module Resolution & Graph: {'PASSED' if build_ok else 'FAILED'}")

    if not (val_ok and build_ok):
        sys.exit(1)


if __name__ == "__main__":
    main()
