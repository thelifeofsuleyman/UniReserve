"""Final submission structure and PDF check; does not imply a user study occurred."""
from __future__ import annotations
from pathlib import Path
import re
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
required=[
    'README.md','requirements-dev.txt',
    'docs/requirements/SRS-v1.md','docs/requirements/USE_CASES-v1.md',
    'docs/requirements/EXISTING_SYSTEMS_REVIEW.md',
    'docs/diagrams/README.md','docs/traceability/MATRIX.md',
    'docs/testing/TEST_PLAN.md','docs/testing/TEST_CASES.md',
    'docs/testing/M6_TEST_REPORT.md','docs/testing/M6_PERFORMANCE_REPORT.md',
    'docs/testing/DEFECT_LOG.md','docs/change-management/CR-001-visual-availability.md',
    'docs/process/ISSUES.md','docs/process/SELF_REVIEW_CHECKLIST.md',
    'docs/reflection/REFLECTION_DRAFT.md',
    'scripts/run_tests.py','scripts/validate_models.py',
    'scripts/validate_traceability.py', 'scripts/measure_latency.py',
    'src/unireserve/web/app.py','tests/test_booking_service.py',
]
for name in required:
    assert (ROOT/name).is_file(), f'Missing required artifact: {name}'

for ext in ('puml','png','svg'):
    folder=ROOT/'docs/diagrams'/('source' if ext=='puml' else 'rendered')
    names=list(folder.glob('*.'+ext))
    assert len(names)==16,f'Expected 16 {ext}, found {len(names)}'

pdfs=[
'01_Requirements_Specification.pdf','02_Analysis_Design_Models.pdf',
'03_Test_Plan_and_Report.pdf','04_Traceability_Matrix.pdf',
'05_Process_Evidence.pdf','06_Individual_Reflection_DRAFT.pdf']
texts={}
for pdf in pdfs:
    target=ROOT/'docs/submission'/pdf
    assert target.exists() and target.stat().st_size>3000, f'Missing/empty PDF: {pdf}'
    reader=PdfReader(target)
    assert len(reader.pages)>=1,pdf
    texts[pdf]='\n'.join(page.extract_text() or '' for page in reader.pages)
    print(f'PDF verified: {pdf} ({len(reader.pages)} pages)')
assert len(PdfReader(ROOT/'docs/submission/02_Analysis_Design_Models.pdf').pages)==16
assert 1<=len(PdfReader(ROOT/'docs/submission/06_Individual_Reflection_DRAFT.pdf').pages)<=2
assert all(x in texts[pdfs[0]] for x in ('LibCal','Skedda','FR-001','UC-01')), 'SRS missing required appendices/UCs'
assert all(x in texts[pdfs[2]] for x in ('TC-001','TC-036','Defect')), 'Test PDF incomplete'
assert all(x in texts[pdfs[3]] for x in ('FR-001','FR-011','NFR-006')), 'Traceability PDF incomplete'
assert all(x in texts[pdfs[4]] for x in ('PR #1','PR #7','Checklist')), 'Process PDF incomplete'
assert 'AI assistance disclosure' in texts[pdfs[5]], 'Reflection must disclose AI'

srs=(ROOT/'docs/requirements/SRS-v1.md').read_text(encoding='utf-8')
assert len(re.findall(r'^\|\s*FR-\d{3}\s*\|\s*Must\s*\|',srs,re.M))==11
assert len(re.findall(r'^\|\s*NFR-\d{3}\s*\|',srs,re.M))==8
print('Final submission structure PASS: 6 PDFs, 16 diagram sources, 32 exports, 11 traced Musts.')
