"""Deterministic coursework PDF exports from the repository's Markdown and UML.

Run from repository root with Python 3.11+: pip install reportlab pillow pypdf
Exports include the original source comparison appendix and remain reviewable.
"""
from __future__ import annotations

from html import escape
from pathlib import Path
import re
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                 LongTable, TableStyle, KeepTogether, XPreformatted)
from reportlab.pdfgen import canvas
from PIL import Image as PillowImage
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'submission'
OUT.mkdir(parents=True, exist_ok=True)

REGULAR = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
BOLD = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
if REGULAR.exists() and BOLD.exists():
    pdfmetrics.registerFont(TTFont('UniSans', str(REGULAR)))
    pdfmetrics.registerFont(TTFont('UniSansBold', str(BOLD)))
    pdfmetrics.registerFontFamily('UniSans', normal='UniSans', bold='UniSansBold', italic='UniSans', boldItalic='UniSansBold')
    FONT, BOLDFONT = 'UniSans', 'UniSansBold'
else:
    FONT, BOLDFONT = 'Helvetica', 'Helvetica-Bold'
INK = colors.HexColor('#17362F')
TEAL = colors.HexColor('#31715B')
LIGHT = colors.HexColor('#EFF4EF')
MUTED = colors.HexColor('#617069')
BORDER = colors.HexColor('#DAE4DE')

styles = {
    'body':ParagraphStyle('BodyUni',fontName=FONT,fontSize=8.7,leading=13,spaceAfter=5,textColor=INK,splitLongWords=True),
    'tiny':ParagraphStyle('TinyUni',fontName=FONT,fontSize=7.4,leading=10,spaceAfter=3,textColor=INK,splitLongWords=True),
    'h1':ParagraphStyle('H1Uni',fontName=BOLDFONT,fontSize=17,leading=23,spaceBefore=13,spaceAfter=10,textColor=INK),
    'h2':ParagraphStyle('H2Uni',fontName=BOLDFONT,fontSize=12,leading=16,spaceBefore=13,spaceAfter=6,textColor=TEAL),
    'h3':ParagraphStyle('H3Uni',fontName=BOLDFONT,fontSize=9.7,leading=14,spaceBefore=9,spaceAfter=4,textColor=INK),
    'cover':ParagraphStyle('CoverUni',fontName=BOLDFONT,fontSize=24,leading=31,spaceAfter=18,textColor=INK),
    'small':ParagraphStyle('SmallUni',fontName=FONT,fontSize=8,leading=11,spaceAfter=4,textColor=MUTED),
    'cell':ParagraphStyle('CellUni',fontName=FONT,fontSize=7.1,leading=10,textColor=INK,splitLongWords=True),
    'cellbold':ParagraphStyle('CellBoldUni',fontName=BOLDFONT,fontSize=7.1,leading=10,textColor=INK,splitLongWords=True),
    'code':ParagraphStyle('CodeUni',fontName='Courier',fontSize=7.4,leading=10.4,textColor=INK,leftIndent=8,rightIndent=8,spaceBefore=3,spaceAfter=6),
}


def rich(text: str) -> str:
    """Conservative inline Markdown --> Paragraph markup (escape before tags)."""
    txt = escape(text.strip())
    txt = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<u>\1</u>', txt)
    txt = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', txt)
    txt = re.sub(r'`([^`]+)`',r'<font name="Courier">\1</font>',txt)
    txt = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<i>\1</i>', txt)
    # Paragraph recognizes only a limited set of entity names; normalize common ones.
    return txt.replace('&amp;nbsp;', ' ')


def paragraph(text: str, kind: str='body') -> Paragraph:
    return Paragraph(rich(text) or ' ', styles[kind])


def row_cells(line: str) -> list[str]:
    return [v.strip() for v in line.strip().strip('|').split('|')]


def is_separator(items: list[str]) -> bool:
    return bool(items) and all(re.match(r'^:?-{3,}:?$', x.strip()) for x in items)


def table_to_flowables(lines: list[str], wide: bool = False):
    headers = row_cells(lines[0]); entries = [row_cells(x) for x in lines[1:]]
    entries = [x for x in entries if not is_separator(x)]
    if not headers or not entries:
        return []
    if len(headers) > 5:
        # Wide tracing/case tables are more readable as labeled records in a PDF.
        out=[]
        for n,entry in enumerate(entries):
            fields = []
            for i,label in enumerate(headers):
                value = entry[i] if i<len(entry) else ''
                if value:
                    fields.append(paragraph(f'**{label}:** {value}', 'tiny'))
            if not fields: continue
            out.append(KeepTogether([Spacer(1,5), *fields, Spacer(1,5)]))
        return out
    width = (landscape(A4)[0] if wide else A4[0]) - 2*35*mm
    counts = [max(7, max(len(v[i]) for v in entries if i<len(v)) if any(i<len(v) for v in entries) else 7)
              for i in range(len(headers))]
    # Bound wide free-text columns while preserving readable identifiers.
    weights=[min(46,max(12,min(n,46))) for n in counts]
    # Prefer narrow ID/status columns.
    for i,h in enumerate(headers):
        if h.lower() in ('id','fr','nfr','status','result','priority'):
            weights[i] = 12
    total=sum(weights)
    widths=[width*w/total for w in weights]
    payload=[[paragraph(h,'cellbold') for h in headers]]
    for entry in entries:
        payload.append([paragraph(entry[i] if i<len(entry) else '','cell') for i in range(len(headers))])
    table=LongTable(payload,colWidths=widths,repeatRows=1,hAlign='LEFT',splitByRow=1)
    table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),LIGHT),('LINEBELOW',(0,0),(-1,0),.7,TEAL),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F8FAF7')]),
        ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),
        ('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5),
        ('BOTTOMPADDING',(0,0),(-1,-1),5),('LINEBELOW',(0,1),(-1,-1),.25,BORDER)
    ]))
    return [Spacer(1,5),table,Spacer(1,10)]


def md_to_story(raw: str, *, wide: bool=False):
    lines=raw.splitlines()
    story=[];i=0;para=[];incode=False;code=[]
    def flush():
        nonlocal para
        if para:
            story.append(paragraph(' '.join(x.strip() for x in para)))
            para=[]
    while i<len(lines):
        line=lines[i]
        if line.strip().startswith('```'):
            flush()
            if incode:
                story.append(XPreformatted(escape('\n'.join(code)),styles['code']))
                code=[]; incode=False
            else: incode=True
            i+=1;continue
        if incode: code.append(line);i+=1;continue
        if line.startswith('|') and '|' in line[1:]:
            flush();grid=[]
            while i<len(lines) and lines[i].startswith('|'):
                grid.append(lines[i]);i+=1
            story.extend(table_to_flowables(grid,wide=wide))
            continue
        if line.startswith('# '):
            flush();story.append(paragraph(line[2:],'h1'))
        elif line.startswith('## '):
            flush();story.append(paragraph(line[3:],'h2'))
        elif line.startswith('### '):
            flush();story.append(paragraph(line[4:],'h3'))
        elif line.startswith('---'):
            flush();story.append(Spacer(1,8))
        elif re.match(r'^\s*(?:[-*]|\d+\.)\s+',line):
            flush();story.append(paragraph('• '+re.sub(r'^\s*(?:[-*]|\d+\.)\s+','',line)))
        elif line.startswith('> '):
            flush();story.append(paragraph('NOTE: '+line[2:],'small'))
        elif not line.strip():
            flush()
        else:
            para.append(line)
        i+=1
    flush()
    return story


def footer(pdf: canvas.Canvas, doc, name: str):
    pdf.setStrokeColor(BORDER);pdf.line(doc.leftMargin,15*mm,doc.pagesize[0]-doc.rightMargin,15*mm)
    pdf.setFont(FONT,7);pdf.setFillColor(MUTED)
    pdf.drawString(doc.leftMargin,11*mm,'UniReserve  /  '+name)
    pdf.drawRightString(doc.pagesize[0]-doc.rightMargin,11*mm,f'Page {doc.page}')


def build_markdown_pdf(output: str, title: str, chapters: list[tuple[str,str]], *,cover: bool=True, compact: bool=False, landscape_mode: bool=False):
    size=landscape(A4) if landscape_mode else A4
    margin=35*mm if landscape_mode else 18*mm
    if landscape_mode: margin=16*mm
    if compact: margin=17*mm
    doc=SimpleDocTemplate(str(OUT/output),pagesize=size,leftMargin=margin,rightMargin=margin,
                          topMargin=21*mm,bottomMargin=20*mm,title=title,author='Suleyman Shafizada / UniReserve')
    story=[]
    if cover:
        story += [Spacer(1,18*mm),paragraph('UNIRESERVE / SOFTWARE ENGINEERING','small'),
                  paragraph(title,'cover'),paragraph('Suleyman Shafizada | Group m666i1 | 23 November 2026','small'),
                  paragraph('Individual Project: Equipment and Room Rental System','body'),
                  paragraph('Submission deadline: 2 December 2026','small'),PageBreak()]
    else:
        story += [paragraph(title,'h1'),paragraph('Suleyman Shafizada / m666i1 / 23 November 2026','small')]
    for idx,(label,filename) in enumerate(chapters):
        if idx>0: story.append(PageBreak())
        source=ROOT/filename
        if not source.is_file(): raise FileNotFoundError(source)
        story.append(paragraph(label,'h2'))
        story.extend(md_to_story(source.read_text(encoding='utf-8'),wide=landscape_mode))
    doc.build(story,onFirstPage=lambda c,d:footer(c,d,title),onLaterPages=lambda c,d:footer(c,d,title))
    return OUT/output

DIAGRAM_RATIONALE = [
'Six actor-facing use cases and their role boundaries; admission to admin workflows is restricted.',
'Conceptual User, Resource, Reservation and ReservationEvent entities with one-to-many history.',
'Pending approval does not block time; only confirmed reservations do. Invalid transitions are excluded.',
'Four conceptual entities and their relationships independent of SQL storage types.',
'3NF implementation columns, PKs, FKs and referential links; cross-row interval overlap requires a transaction.',
'Service Layer, Repository and Unit of Work concepts; actual ORM/context-manager implementation differences are documented.',
'Layered Flask -> services -> domain/persistence -> SQLite architecture; modular monolith fits a small prototype.',
'UC-01 login, invalid credential alternative and session logout.',
'UC-02 read-only catalogue/availability check with invalid/disabled alternatives.',
'UC-03 atomic booking request and conflict rejection using BEGIN IMMEDIATE.',
'UC-04 reservation cancellation conditional on ownership and start time.',
'UC-05 admin approval/rejection with stale-state and overlapping-confirmation alternatives.',
'UC-06 catalogue changes restricted to admin and validated before write.',
'CR-001 authenticated 2D Studio read-only snapshot/30-second refresh; no physical sensors or surveyed coordinates.',
'CR-002 normalized Space and SpaceClosure extension for seat-level booking, 7-bit weekday mask, and preserved historical resource FKs.',
'CR-002 booking/approval rechecks weekday hours, room closure and resource-specific confirmed overlap under a SQLite write transaction.',
]


def build_models_pdf():
    out=OUT/'02_Analysis_Design_Models.pdf'
    images=sorted((ROOT/'docs/diagrams/rendered').glob('*.png'))
    if len(images)!=16:
        raise ValueError(f'Expected 16 rendered model PNGs, got {len(images)}')
    cv=canvas.Canvas(str(out),pagesize=landscape(A4))
    W,H=landscape(A4)
    for index,path in enumerate(images):
        cv.setFillColor(INK);cv.setFont(BOLDFONT,17)
        cv.drawString(20*mm,H-20*mm,f'FIGURE {index+1:02d}  /  '+path.stem.replace('-',' '))
        cv.setFont(FONT,9);cv.setFillColor(MUTED)
        cv.drawRightString(W-20*mm,H-21*mm,'UNIRESERVE  /  DESIGN MODELS')
        with PillowImage.open(path) as im:
            iw,ih=im.size
        max_w=W-42*mm;max_h=H-72*mm
        factor=min(max_w/iw,max_h/ih)
        dw,dh=iw*factor,ih*factor
        cv.drawImage(str(path),(W-dw)/2,30*mm+(max_h-dh)/2,dw,dh,preserveAspectRatio=True,mask='auto')
        description=DIAGRAM_RATIONALE[index]
        para=paragraph(description,'body')
        _,ph=para.wrap(W-40*mm,50*mm)
        para.drawOn(cv,20*mm,24*mm-ph)
        cv.setStrokeColor(BORDER);cv.line(20*mm,15*mm,W-20*mm,15*mm)
        cv.setFont(FONT,8);cv.setFillColor(MUTED)
        cv.drawString(20*mm,11*mm,'Source: docs/diagrams/source/'+path.stem+'.puml')
        cv.drawRightString(W-20*mm,11*mm,f'Page {index+1} / {len(images)}')
        cv.showPage()
    cv.save();return out


def verify():
    needed=[
        '01_Requirements_Specification.pdf','02_Analysis_Design_Models.pdf',
        '03_Test_Plan_and_Report.pdf','04_Traceability_Matrix.pdf',
        '05_Process_Evidence.pdf','06_Individual_Reflection_DRAFT.pdf'
    ]
    for filename in needed:
        p=OUT/filename
        if not p.exists() or p.stat().st_size<3000:raise AssertionError(f'Empty PDF {filename}')
        reader=PdfReader(str(p))
        if not reader.pages:raise AssertionError(f'PDF no pages {filename}')
        if filename=='02_Analysis_Design_Models.pdf' and len(reader.pages)!=16:
            raise AssertionError(f'Model diagrams PDF should have 16 pages: {len(reader.pages)}')
        if filename=='06_Individual_Reflection_DRAFT.pdf' and not (1<=len(reader.pages)<=2):
            raise AssertionError(f'Reflection draft must be 1-2 pages: {len(reader.pages)}')
        if filename!='02_Analysis_Design_Models.pdf':
            full='\n'.join(x.extract_text() or '' for x in reader.pages)
            if len(full)<300:raise AssertionError(f'Searchable text missing in {filename}')
        print(f'PDF PASS: {filename}: {len(reader.pages)} pages, {p.stat().st_size} bytes')


def main():
    build_markdown_pdf('01_Requirements_Specification.pdf','A / Requirements Specification',[
       ('Core SRS','docs/requirements/SRS-v1.md'),
       ('Six Detailed Use Cases','docs/requirements/USE_CASES-v1.md'),
       ('Appendix A: Existing Systems — LibCal and Skedda','docs/requirements/EXISTING_SYSTEMS_REVIEW.md'),
       ('Appendix B: AzTU-inspired booking change','docs/change-management/CR-002-aztu-seat-reservations.md'),
       ('Appendix C: CR-003 UI and fair-use change','docs/change-management/CR-003-ux-and-integrity.md')])
    build_models_pdf()
    build_markdown_pdf('03_Test_Plan_and_Report.pdf','C / Test Plan and Report',[
       ('Testing Plan','docs/testing/TEST_PLAN.md'),
       ('Executed Test Cases','docs/testing/TEST_CASES.md'),
       ('Verified Testing Report','docs/testing/M6_TEST_REPORT.md'),
       ('Measured Performance Evidence','docs/testing/M6_PERFORMANCE_REPORT.md'),
       ('Defect Log','docs/testing/DEFECT_LOG.md'),
       ('AzTU Seat and Timetable Regression','docs/testing/CR-002_TEST_ADDENDUM.md'),
       ('CR-003 UI and Booking Regression','docs/testing/CR-003_TEST_ADDENDUM.md')])
    build_markdown_pdf('04_Traceability_Matrix.pdf','D / Requirements Traceability',[
       ('Traceability and Explicit Gaps','docs/traceability/MATRIX.md'),
       ('CR-002 Seat and Lab Rule Traces','docs/traceability/CR-002-TRACEABILITY.md'),
       ('CR-003 UI and Fair-use Traces','docs/traceability/CR-003-TRACEABILITY.md')],landscape_mode=True)
    build_markdown_pdf('05_Process_Evidence.pdf','F / Process and Review Evidence',[
       ('Process History','docs/process/PROCESS_EVIDENCE.md'),
       ('Completed Self-Review Checklist','docs/process/SELF_REVIEW_CHECKLIST.md'),
       ('Issue Board','docs/process/ISSUES.md'),
       ('Owner Feedback and Change Analysis','docs/change-management/CR-001-visual-availability.md'),
       ('CR-002 AzTU Operational Change','docs/change-management/CR-002-aztu-seat-reservations.md'),
       ('CR-003 Owner Feedback and Logic Audit','docs/change-management/CR-003-ux-and-integrity.md')])
    build_markdown_pdf('06_Individual_Reflection_DRAFT.pdf','G / Individual Reflection — Draft for Review',[
       ('Personal Reflection — Draft','docs/reflection/REFLECTION_DRAFT.md')],cover=False,compact=True)
    verify()

if __name__=='__main__':main()
