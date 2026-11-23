"""Static cross-artifact traceability validation for all Must requirements."""
from __future__ import annotations
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
srs=(ROOT/'docs/requirements/SRS-v1.md').read_text(encoding='utf-8')
mat=(ROOT/'docs/traceability/MATRIX.md').read_text(encoding='utf-8')
case_text=(ROOT/'docs/testing/TEST_CASES.md').read_text(encoding='utf-8')
ids=re.findall(r'^\|\s*(FR-\d{3})\s*\|\s*Must\s*\|',srs,re.M)
assert len(ids)==11, f'Expected 11 Must FR, got {len(ids)}'
rows={re.match(r'^\|\s*(FR-\d{3})\s*\|',x).group(1):x
      for x in mat.splitlines() if re.match(r'^\|\s*(FR-\d{3})\s*\|',x)}
assert set(ids)<=set(rows),f'Missing Must rows: {set(ids)-set(rows)}'
cases=set(re.findall(r'\bTC-\d{3}\b',case_text))
for req in ids:
 row=rows[req]
 cells=[x.strip() for x in row.strip('|').split('|')]
 assert len(cells)==6, (req,'Expected 6 columns')
 _,uc,design,code,case_ids,status=cells
 assert 'UC-' in uc, (req,'No use case')
 diagrams=re.findall(r'[\w-]+\.puml',design)
 assert diagrams, (req,'No design')
 for diagram in diagrams:
  assert (ROOT/'docs/diagrams/source'/diagram).exists(),(req,'Missing UML',diagram)
 paths=re.findall(r'`([^`]+\.(?:py|html))`',code)
 assert paths, (req,'No code path')
 for path in paths:
  assert (ROOT/path).is_file(),(req,'Missing code',path)
 refs=re.findall(r'TC-\d{3}',case_ids)
 assert refs and set(refs)<=cases, (req,'Unlisted tests')
 for tc in refs:
  case_row=next((x for x in case_text.splitlines() if x.startswith('| '+tc+' |')),None)
  assert case_row and req in case_row, (req,'TC does not trace back',tc)
 assert status=='PASS', (req,'Not verified')
print(f'Traceability PASS: {len(ids)} Must requirements have UC, UML, source and named CI tests.')
