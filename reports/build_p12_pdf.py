"""Typeset the P12 closeout from audited results, without enumerating factors.

The companion LaTeX source is retained; the built-in compiler was unavailable.
This PDF edition uses ReportLab and the same results and provenance.
"""
import json
from xml.sax.saxutils import escape
from matplotlib.font_manager import FontProperties, findfont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from mf.protocol import ROOT, digest


def build():
    audit_path=ROOT/'results/Vault_S2_full/audit.json'
    audit=json.loads(audit_path.read_text(encoding='utf-8'))
    assert audit['external_review']['attestation']['operator_reports_exact_hash_match']
    assert audit['external_review']['attestation']['external_prediction_receipt_before_computation'] is False
    records=audit['records']; r2=records['sealed_region_2']; full=records['enlarged_design']
    assert digest(ROOT/'predictions/Vault_S2_L001_L002_L003.json')==audit['registration']['prediction_sha256']
    for name,weight,style in [('Body','normal','normal'),('BodyB','bold','normal'),('BodyI','normal','italic')]:
        pdfmetrics.registerFont(TTFont(name,findfont(FontProperties(family='DejaVu Serif',weight=weight,style=style))))
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyB',italic='BodyI',boldItalic='BodyB')
    navy=colors.HexColor('#142D46'); gray=colors.HexColor('#53616E'); pale=colors.HexColor('#EDF2F6')
    styles={
        'body':ParagraphStyle('body',fontName='Body',fontSize=10.1,leading=14.3,spaceAfter=7,textColor=colors.HexColor('#17222C')),
        'small':ParagraphStyle('small',fontName='Body',fontSize=8.4,leading=11.5,spaceAfter=6),
        'abstract':ParagraphStyle('abstract',fontName='Body',fontSize=9.4,leading=13,spaceAfter=10),
        'title':ParagraphStyle('title',fontName='BodyB',fontSize=19,leading=23,textColor=navy,spaceAfter=12),
        'h1':ParagraphStyle('h1',fontName='BodyB',fontSize=13,leading=17,textColor=navy,spaceBefore=8,spaceAfter=9),
        'h2':ParagraphStyle('h2',fontName='BodyB',fontSize=10.4,leading=14,textColor=navy,spaceBefore=5,spaceAfter=5),
        'formula':ParagraphStyle('formula',fontName='Body',fontSize=10,leading=15,leftIndent=12,spaceAfter=9),
        'cell':ParagraphStyle('cell',fontName='Body',fontSize=8.2,leading=11),
        'head':ParagraphStyle('head',fontName='BodyB',fontSize=8.1,leading=10.5,textColor=navy),
        'mono':ParagraphStyle('mono',fontName='Courier',fontSize=7.6,leading=10,spaceAfter=7),
    }
    story=[]
    def p(text,kind='body'): story.append(Paragraph(text,styles[kind]))
    def table(rows,widths):
        prepared=[[Paragraph(escape(str(c)),styles['head' if i==0 else 'cell']) for c in row] for i,row in enumerate(rows)]
        t=Table(prepared,colWidths=widths,hAlign='LEFT',repeatRows=1)
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),pale),('LINEABOVE',(0,0),(-1,0),0.8,navy),
                              ('LINEBELOW',(0,0),(-1,0),0.45,gray),('LINEBELOW',(0,-1),(-1,-1),0.7,navy),
                              ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
                              ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
                              ('VALIGN',(0,0),(-1,-1),'TOP')]))
        story.extend([t,Spacer(1,10)])
    def newpage(): story.append(PageBreak())
    labels={'sealed_region_2':'Region 2','extension':'Extension','enlarged_design':'Full design'}
    def fmt(v): return f'{v:,.3f}'

    p('Exact Mersenne Factor Censuses<br/>and a Finite Bernoulli Multiplicity Model','title')
    p('<b>Chris Miki</b><br/>4 October 2026 | P12 technical report, revised','small')
    p('<b>Abstract.</b> Two independent exhaustive programs found 487,025 prime-factor pairs for prime exponents '
      '10,000,001 ≤ p ≤ 30,000,000 and k ≤ 10,000 in q = 2kp + 1. Independent checkers accepted every pair. '
      'A user-relayed external operator confirmation reports an exact match to the original region 2 withheld '
      'census hash and all four summary cells. A zero-fit Poisson-binomial model improves the frozen composite '
      'score over the project\'s Poisson model by 35.487 on region 2 and 69.789 on the full design. Smaller '
      'residuals remain. This confirms established heuristics, rather than establishing a new law. Prediction-first '
      'ordering has local Git evidence, but no independent pre-run fingerprint receipt.','abstract')
    p('1. Finite problem and exact computation','h1')
    p('For prime p, put M<sub>p</sub> = 2<super>p</super> - 1 and let I<sub>p,k</sub> indicate that '
      'q = 2kp + 1 is prime and divides M<sub>p</sub>. Write J<sub>p</sub> = Σ<sub>k≤10,000</sub> I<sub>p,k</sub>. '
      'Each census pair (p,k) is counted once. The reported cells are total pairs C = Σ<sub>p</sub>J<sub>p</sub>, '
      'A<sub>j</sub> = #{p : J<sub>p</sub> ≥ j} for j = 1, 2, and the maximum M = max<sub>p</sub>J<sub>p</sub>.')
    p('Region 2 is p in [10,000,001, 20,000,000]; the extension is [20,000,001, 30,000,000]. '
      'Endpoints are inclusive and K = 10,000 throughout. The full design is their union.')
    rows=[['Scope','Prime exponents','Factors C','A₁','A₂','Max.']]
    for s,n in [('sealed_region_2',606028),('extension',587252),('enlarged_design',1193280)]:
        o=records[s]['observed']; rows.append([labels[s],f'{n:,}',f'{o["total"]:,}',f'{o["at_least_one"]:,}',f'{o["at_least_two"]:,}',o['maximum']])
    table(rows,[91,93,81,75,72,43])
    p('The two C programs use different loop orders, modular arithmetic and sieving implementations. '
      'All 40 contiguous chunks agreed byte for byte. Fresh Python and independent C checks validated '
      'prime exponents, prime factors and divisibility. The final audit checked coverage, source provenance, '
      'canonical pairs, hashes, certificates and an independent summary recount. Region 1 was not rerun.')
    p('2. Relationship to established work','h1')
    p('Shanks and Kravitz studied divisor counts indexed by k [1]. Wagstaff gives the pair-weight heuristic '
      'and, on page 387, equation (4), already uses a product of no-factor probabilities [2]. '
      'L003 corrects this project\'s L001 Poisson approximation, not Wagstaff\'s full treatment. '
      'The Poisson-binomial distribution is the standard law of independent Bernoulli sums [3].')

    newpage();p('3. Frozen models and prospective design','h1')
    p('L001 and L003 share the following pair mean for k ≡ 0 or -p (mod 4); other k have weight zero. '
      'The product runs over odd prime divisors r of k.')
    p('w<sub>p,k</sub> = [2C₂ / (k log(2kp))] ∏<sub>r|k, r&gt;2</sub> (r - 1)/(r - 2),<br/>'
      'C₂ = 0.6601618158468696, &nbsp; μ<sub>p</sub> = Σ<sub>k</sub>w<sub>p,k</sub>.','formula')
    p('These are heuristic pair means. L001 models J<sub>p</sub> as Poisson(μ<sub>p</sub>), giving '
      'E A₁ = Σ<sub>p</sub>(1 - exp(-μ<sub>p</sub>)) and '
      'E A₂ = Σ<sub>p</sub>[1 - exp(-μ<sub>p</sub>)(1 + μ<sub>p</sub>)].')
    p('<b>L003</b> gives each candidate k one independent Bernoulli event of probability w<sub>p,k</sub>, '
      'with no fitted parameters. Its probability-generating function and first probabilities are')
    p('G<sub>p</sub>(z) = ∏<sub>k≤10,000</sub>(1 - w<sub>p,k</sub> + w<sub>p,k</sub>z),<br/>'
      'P<sub>p,0</sub> = G<sub>p</sub>(0), &nbsp; P<sub>p,1</sub> = P<sub>p,0</sub> Σ<sub>k</sub>w<sub>p,k</sub>/(1 - w<sub>p,k</sub>),<br/>'
      'E A₁ = Σ<sub>p</sub>(1 - P<sub>p,0</sub>), &nbsp; E A₂ = Σ<sub>p</sub>(1 - P<sub>p,0</sub> - P<sub>p,1</sub>).','formula')
    p('The mean remains μ<sub>p</sub>, but the variance is μ<sub>p</sub> - Σ<sub>k</sub>w<sub>p,k</sub>². '
      'Assuming independence across exponents and denoting the per-exponent CDF by F<sub>p</sub>, '
      'E M = Σ<sub>j≥0</sub>[1 - ∏<sub>p</sub>F<sub>p</sub>(j)]. Coefficient recursion through degree 24, '
      'tail bounds, direct small examples and 24/32-node interpolation checks validated numerical accuracy '
      'before commitment. The independence assumptions themselves remain heuristic.')
    p('N0 is a small-prime-sieved pair heuristic. L002 multiplies N0 by fixed local correction factors '
      'for primes 53 ≤ r ≤ 997. Both retain Poisson multiplicities; neither fits the observed data. '
      'Exact definitions and source hashes accompany the prediction file.')
    p('Score and pre-run separation check','h2')
    p('The frozen score is D(y,ν) = Σ<sub>c</sub> 2[ν<sub>c</sub> - y<sub>c</sub> + '
      'y<sub>c</sub> log(y<sub>c</sub>/ν<sub>c</sub>)], with the usual zero-count limit. '
      'It includes total factors, 14 dyadic k buckets, all residues modulo 3, 4, 5, 8 and 12, '
      'A₁, A₂, and M once. These cells overlap: the score is a composite diagnostic, not an '
      'independent likelihood ratio or calibrated significance test. The fixed winning margin is 14.')
    p('For competing means a and b, the expected gain of a over b when a is true is '
      '2Σ<sub>c</sub>[b<sub>c</sub> - a<sub>c</sub> + a<sub>c</sub> log(a<sub>c</sub>/b<sub>c</sub>)]. '
      'Both truth directions had to reach 14. This is an expected-separation rule, not an 80% power calculation.')
    table([['Comparison / scope','Expected gains in both directions'],
           ['N0 / L002, region 2','10.473 / 10.464 - insufficient'],
           ['N0 / L002, full design','20.342 / 20.324'],
           ['L001 / L003, full design','34.593 / 34.478']],[236,219])
    p('The extension was therefore chosen before commitment and computation. All six primary law pairs '
      'pass the rule on the full design. The original region 2 remains a separate sealed scope; '
      'the extension is not operator sealed. The union is not an independent replication.','small')

    newpage();p('4. Results and the remaining discrepancy','h1')
    p('L001 and L003 have identical factor-count expectations. Predicted maxima are expectations, not modes.')
    rows=[['Scope / cell','Observed','L001','L003']]
    for s in ('sealed_region_2','enlarged_design'):
        r=records[s]
        for c,label in [('total','factors'),('at_least_one','A₁'),('at_least_two','A₂'),('maximum','maximum')]:
            rows.append([labels[s]+' / '+label,f'{r["observed"][c]:,}',fmt(r['predictions']['L001'][c]),fmt(r['predictions']['L003'][c])])
    table(rows,[161,88,103,103])
    rows=[['Law','Region 2 deviance','Full deviance','Full gain over N0']]
    ds=full['scores']['descriptive_composite']['deviances']; d2=r2['scores']['descriptive_composite']['deviances']
    for law in ('N0','L001','L002','L003'):
        rows.append([law,fmt(d2[law]),fmt(ds[law]),'-' if law=='N0' else fmt(ds['N0']-ds[law])])
    table(rows,[60,133,116,146])
    p('All three laws beat N0 on the powered full design. L003 beats L001 by <b>35.487</b> on region 2 '
      'and <b>69.789</b> on the full design. Multiplicity-only deviances fall from 40.044 to 4.557 and '
      'from 79.055 to 9.266, respectively; factor-count contributions cancel. The region 2 N0/L002 '
      'contrast gains only 13.082 and remains underpowered, so has no standalone passing verdict.')
    rows=[['L003: observed minus predicted','A₁ residual','A₂ residual']]
    for s in ('sealed_region_2','extension','enlarged_design'):
        r=records[s];rows.append([labels[s],*(f'{r["observed"][c]-r["predictions"]["L003"][c]:+,.3f}' for c in ('at_least_one','at_least_two'))])
    table(rows,[255,100,100])
    p('The two disjoint bands have residuals of the same sign. Their sum is the combined residual, '
      'not a third independent observation. A₁ and A₂ count <i>at least</i> one and two factors; '
      'their difference counts exactly one. An exactly-two discrepancy cannot be inferred from these cells alone.')
    p('Full-design signed prediction errors, relative to observed counts, are +0.0846% for total factors, '
      '-0.2200% for A₁ and +0.9956% for A₂. Thus 0.1-0.3% is not uniform accuracy across cells. '
      'The finite Bernoulli correction explains much of the original discrepancy, but not all of it. '
      'Reviewer-supplied sigma estimates are not treated as calibrated tests: their covariance calculation '
      'was not supplied. These results establish neither a new arithmetic repulsion law nor that every '
      'residual is ordinary noise. No law was refitted after observing these outcomes.','small')

    newpage();p('5. Sealed comparisons and provenance','h1')
    p('The local record places prediction commitment at 18:40:13 UTC on 3 October 2026, before the '
      'census began at approximately 18:59 UTC. The user authorized the full design after receiving the '
      'fingerprint in this chat. Models, predictions, scoring and prospective bounds stayed fixed. '
      'The completed evidence was saved in Git commit b1540d0; the prediction commit is '
      '<font name="Courier" size="8">0a3a73847f3f533dae5fcface0c0abd5099801cb</font>.')
    p('A later user-relayed operator message confirms an exact match to the withheld region 2 census '
      'hash and all four cells: 250,614 factors, A₁ = 206,852, A₂ = 38,568 and maximum 5. '
      'The local agent did not inspect the original withheld file or independently establish the '
      'operator\'s identity.')
    p('Earlier region 1: reported confirmation','h2')
    p('The user previously relayed that an independent operator matched the v0.2 region 1 census '
      'hash to the sealed hash exactly and scored L001 against withheld values. SOURCE.md, item 12, '
      'records this external statement. The named document REVIEW_VAULT_S1_L001.md remains unavailable '
      'to this checkout as of 4 October 2026, so its full hash, exact score and review qualifications '
      'cannot be transcribed or independently checked here. Region 1 was not rerun.')
    p('A separate post-commit note reports region 1 observations A₁ = 240,726 and A₂ = 56,673 '
      '(SOURCE.md, item 15). These are attributed historical observations, not locally recertified '
      'results; the note\'s approximate L003 estimates are not a preregistered region 1 test. '
      'None of these estimates entered the frozen region 2 predictions.')
    p('<b>Protocol qualification.</b> The operator reports that the prediction fingerprint was not relayed '
      'to them before computation. Prediction-first ordering has local Git and execution evidence, '
      'but no independently witnessed pre-run receipt. The later outcome match does not repair this '
      'missing timestamp. Future sealed tests should obtain a dated custodian receipt for the exact '
      'prediction fingerprint, bounds and scoring rule before enumeration.')
    p('SHA-256 fingerprints','h2')
    p('Canonical census files contain sorted ASCII <font name="Courier">p k</font> rows with LF endings. '
      'The regional files concatenate to the full-design file.','small')
    for label,sha in [('Prediction',audit['registration']['prediction_sha256']),
                      *[(labels[s]+' census',records[s]['output']['sha256']) for s in ('sealed_region_2','extension','enlarged_design')]]:
        p('<b>'+label+'</b>','small');p(sha,'mono')
    p('Native engine work was 1.023741 CPU-hours; checkers, predictions, aggregation and other overhead '
      'are excluded.','small')

    newpage();p('6. Code and data availability','h1')
    p('Code, predictions, complete census outputs, certificates and this report are retained in the local '
      'mersenne-factor-laws Git repository. No public repository URL or archive DOI is recorded in this '
      'version; public access remains pending. No project-wide reuse licence is declared; vendored GNU '
      'mini-gmp retains its accompanying upstream licence texts.','small')
    p('Reproducibility materials','h2')
    p('<b>Code:</b> mf/, laws/, ops/ and tests/ contain both checkers, both engines, models, runner and validation. '
      '<b>Protocol:</b> REGISTRATION.md and POWER_PROTOCOL.md document the design; the frozen prediction '
      'bundle includes source hashes and links to prospective forecasts:','small')
    p('predictions/Vault_S2_L001_L002_L003.json','mono')
    p('<b>Data:</b> runs/Vault_S2_full/ retains both engines\' 40 chunk outputs and execution records. '
      'Its sealed_region_2, extension and enlarged_design subdirectories each contain census.txt, '
      'summary_cells.json and score.json. <b>Evidence:</b> certificates/ stores explicit pairs and '
      'verification records; results/Vault_S2_full/ stores the aggregate audit and tables; SOURCE.md '
      'and data/sources/ record literature and attributed reviews.','small')
    p('Audit the saved experiment','h2')
    p('Use a full, non-shallow checkout with all tracked data and history containing the prediction and '
      'results commits in section 5. A source-only ZIP cannot establish the Git provenance checked by '
      'the audit. From the repository root, with Python 3.10+ and Git available, run:','small')
    p('python -m ops.vault_report','mono')
    p('This checks saved bytes, source provenance, coverage, certificates and counts, recomputes the frozen '
      'scores and refreshes audit outputs. It does not enumerate factors or supply an external timestamp.','small')
    p('Recompute the censuses','h2')
    p('For independent replay, use Python 3.12 (the original run used 3.12.14), Git and GCC or Clang with '
      'C11 and unsigned 128-bit support; Windows uses MinGW-w64. From a separate checkout, run:','small')
    p('python -m pip install -r requirements-research.txt<br/>'
      'python -m ops.build<br/>'
      'python -m unittest discover -s tests -v<br/>'
      'python -m ops.verify','mono')
    p('The last command rechecks every stored certificate with both checkers and re-enumerates every '
      'stored census with both engines, including overlapping regional and union certificates. This '
      'takes substantially more work than the saved-artifact audit. Compare canonical hashes with '
      'section 5; replay is verification, not a new sealed test. No census was rerun for this revision. '
      'Further command details are in README.md.','small')
    p('<b>Conclusion.</b> This bounded P12 comparison is closed as empirical confirmation, with a '
      'documented residual and provenance limitation. No new theorem, law or credited factor is claimed. '
      'These observed bands must not be reused as fresh tests of revised models.','small')
    p('Computational implementation, orchestration and drafting were assisted by OpenAI Codex. '
      'External confirmation is recorded as relayed operator testimony.','small')
    p('References','h2')
    p('[1] D. Shanks and S. Kravitz, <i>On the Distribution of Mersenne Divisors</i>, '
      'Mathematics of Computation 21 (1967). '
      '<link href="https://t5k.org/mersenne/literature/shanksKravitz.html">Primary-paper transcription</link>.','small')
    p('[2] S. S. Wagstaff, Jr., <i>Divisors of Mersenne Numbers</i>, Mathematics of Computation '
      '40 (1983), 385-397. <link href="https://doi.org/10.1090/S0025-5718-1983-0679454-X">'
      'doi:10.1090/S0025-5718-1983-0679454-X</link>.','small')
    p('[3] Y. Hong, <i>On computing the distribution function for the Poisson binomial distribution</i>, '
      'Computational Statistics &amp; Data Analysis 59 (2013), 41-51. '
      '<link href="https://doi.org/10.1016/j.csda.2012.10.006">doi:10.1016/j.csda.2012.10.006</link>.','small')

    out=ROOT/'output/pdf/P12_Chris_Miki.pdf';out.parent.mkdir(parents=True,exist_ok=True)
    def furniture(canvas,doc):
        canvas.saveState(); w,h=A4
        canvas.setStrokeColor(colors.HexColor('#CFD7DE'));canvas.setLineWidth(0.4);canvas.line(70,47,w-70,47)
        canvas.setFont('Body',7.5);canvas.setFillColor(gray)
        canvas.drawString(70,33,'Chris Miki | P12 | Revised 4 October 2026')
        canvas.drawRightString(w-70,33,str(doc.page));canvas.restoreState()
    doc=SimpleDocTemplate(str(out),pagesize=A4,rightMargin=70,leftMargin=70,topMargin=46,bottomMargin=60,
                          title='Exact Mersenne Factor Censuses and a Finite Bernoulli Multiplicity Model',author='Chris Miki')
    doc.build(story,onFirstPage=furniture,onLaterPages=furniture)
    from pypdf import PdfReader
    reader=PdfReader(out)
    evidence={'pdf':str(out.relative_to(ROOT)),'pdf_sha256':digest(out),'pages':len(reader.pages),
              'author':reader.metadata.author,'audit_sha256':digest(audit_path),
              'prediction_sha256':audit['registration']['prediction_sha256'],
              'companion_latex_sha256':digest(ROOT/'reports/P12_Chris_Miki.tex'),
              'pdf_backend':'ReportLab','latex_compilation':'unavailable: built-in host could not find standard directories',
              'visual_review':'pending'}
    (ROOT/'reports/P12_build_record.json').write_text(json.dumps(evidence,sort_keys=True,indent=2)+'\n')
    print(json.dumps(evidence))


if __name__=='__main__': build()
