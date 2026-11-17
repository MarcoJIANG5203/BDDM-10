// Build the integrated IEEE-format Word manuscript (editable master draft).
//
//   npm install docx            (once, in any working directory)
//   NODE_PATH=<dir>/node_modules node paper/word/make_manuscript_docx.js [out.docx]
//
// Layout follows the IEEE conference Word template: US Letter, 0.75"/1" top/bottom and 0.625"
// side margins, two 3.5" columns, Times New Roman 10 pt body. Every number in the text is taken
// from the accepted run 20261105T055420_02d05b15 and the signed content-review package; see
// handoffs/D/2026-11-14_integrated_word_draft.md for the number-to-source list.
const fs = require("fs");
const path = require("path");
const D = require("docx");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, WidthType,
  AlignmentType, BorderStyle, SectionType, TabStopType, LevelFormat, ImportedXmlComponent,
  VerticalAlign,
} = D;

const ROOT = path.resolve(__dirname, "..", "..");
const OUT = process.argv[2] || path.join(ROOT, "paper", "camera-ready", "BDDM2026_manuscript_integrated.docx");
const FONT = "Times New Roman";
const COL = 5040;                       // one column, DXA (3.5 in)
const PAGE = { size: { width: 12240, height: 15840 }, margin: { top: 1080, bottom: 1440, left: 900, right: 900 } };

// ---------------------------------------------------------------------------------------------
// References (metadata as in paper/references.bib; numbering is assigned by first citation).
// ---------------------------------------------------------------------------------------------
const REFS = {
  rubin1987multiple: "D. B. Rubin, *Multiple Imputation for Nonresponse in Surveys*. New York, NY, USA: Wiley, 1987.",
  vanbuuren2011mice: "S. van Buuren and K. Groothuis-Oudshoorn, “mice: Multivariate imputation by chained equations in R,” *Journal of Statistical Software*, vol. 45, no. 3, pp. 1–67, 2011.",
  chow1970optimum: "C. K. Chow, “On optimum recognition error and reject tradeoff,” *IEEE Transactions on Information Theory*, vol. 16, no. 1, pp. 41–46, 1970.",
  geifman2017selective: "Y. Geifman and R. El-Yaniv, “Selective classification for deep neural networks,” in *Advances in Neural Information Processing Systems 30*, 2017.",
  mozannar2020consistent: "H. Mozannar and D. Sontag, “Consistent estimators for learning to defer to an expert,” in *Proceedings of the 37th International Conference on Machine Learning*, PMLR, vol. 119, 2020.",
  angelopoulos2023conformal: "A. N. Angelopoulos and S. Bates, “Conformal prediction: A gentle introduction,” *Foundations and Trends in Machine Learning*, 2023, doi: 10.1561/2200000101.",
  kwon2026conformal: "H. Kwon and D.-J. Kim, “Conformal selective prediction with cost aware deferral for safe clinical triage under distribution shift,” *Scientific Reports*, 2026, doi: 10.1038/s41598-026-40637-w.",
  zaffran2023conformal: "M. Zaffran, A. Dieuleveut, J. Josse, and Y. Romano, “Conformal prediction with missing values,” in *Proceedings of the 40th International Conference on Machine Learning*, PMLR, vol. 202, 2023.",
  he2026safeimpute: "X. He, M. Ai, J. Wang, C. B. Cook, and J. He, “SafeImpute: Reliable clinical data imputation via conformal selection,” in *Proceedings of the 32nd ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2*, 2026, doi: 10.1145/3770855.3817967.",
  wong2026mc2: "K. K. Wong and A. Ajit, “Guarantees that survive a missing scan: Modality-conditional conformal prediction for multimodal medical diagnosis,” in *MICCAI 2026 Satellite Events (Workshops and Challenges), MLMI*, Lecture Notes in Computer Science, vol. 17272, 2026.",
  vovk2005algorithmic: "V. Vovk, A. Gammerman, and G. Shafer, *Algorithmic Learning in a Random World*. New York, NY, USA: Springer, 2005.",
  sadinle2019least: "M. Sadinle, J. Lei, and L. Wasserman, “Least ambiguous set-valued classifiers with bounded error levels,” *Journal of the American Statistical Association*, vol. 114, no. 525, pp. 223–234, 2019.",
  romano2020classification: "Y. Romano, M. Sesia, and E. J. Candès, “Classification with valid and adaptive coverage,” in *Advances in Neural Information Processing Systems 33*, 2020.",
  tibshirani2019covariate: "R. J. Tibshirani, R. F. Barber, E. J. Candès, and A. Ramdas, “Conformal prediction under covariate shift,” in *Advances in Neural Information Processing Systems 32*, 2019.",
  barber2023beyond: "R. F. Barber, E. J. Candès, A. Ramdas, and R. J. Tibshirani, “Conformal prediction beyond exchangeability,” *The Annals of Statistics*, vol. 51, no. 2, pp. 816–845, 2023.",
  li2026deployment: "C. Li, X. Liu, H. Zhang, H. Peng, Y. Ruan, H. Ma, C. Miao, Q. Zhou, X. Qi, and P. Yu, “A deployment audit of release-side risk in conformal triage under prevalence shift,” arXiv:2605.20956v2, 2026.",
  little2019statistical: "R. J. A. Little and D. B. Rubin, *Statistical Analysis with Missing Data*, 3rd ed. Hoboken, NJ, USA: Wiley, 2019.",
  vavaroutas2025squiredl: "S. Vavaroutas, T. Dang, E. Rocheteau, and C. Mascolo, “SQUIREDL: Sparse sequence-to-sequence uncertainty estimation in evidential deep learning,” *ACM Transactions on Computing for Healthcare*, 2025, doi: 10.1145/3723049.",
  reyna2020early: "M. A. Reyna, C. S. Josef, R. Jeter, S. P. Shashikumar, M. B. Westover, S. Nemati, G. D. Clifford, and A. Sharma, “Early prediction of sepsis from clinical data: The PhysioNet/Computing in Cardiology Challenge 2019,” *Critical Care Medicine*, vol. 48, no. 2, pp. 210–217, 2020.",
  goldberger2000physiobank: "A. L. Goldberger *et al.*, “PhysioBank, PhysioToolkit, and PhysioNet: Components of a new research resource for complex physiologic signals,” *Circulation*, vol. 101, no. 23, pp. e215–e220, 2000.",
  singer2016sepsis3: "M. Singer *et al.*, “The third international consensus definitions for sepsis and septic shock (Sepsis-3),” *JAMA*, vol. 315, no. 8, pp. 801–810, 2016.",
};
const citeOrder = [];
function citeNumbers(keys) {
  const nums = keys.map((k) => {
    if (!REFS[k]) throw new Error(`Unknown citation key ${k}`);
    if (!citeOrder.includes(k)) citeOrder.push(k);
    return citeOrder.indexOf(k) + 1;
  }).sort((a, b) => a - b);
  const parts = [];
  for (let i = 0; i < nums.length;) {
    let j = i;
    while (j + 1 < nums.length && nums[j + 1] === nums[j] + 1) j++;
    if (j - i >= 2) parts.push(`[${nums[i]}]–[${nums[j]}]`);
    else for (let k = i; k <= j; k++) parts.push(`[${nums[k]}]`);
    i = j + 1;
  }
  return parts.join(", ");
}

// ---------------------------------------------------------------------------------------------
// Inline markup: **bold**, *italic*, _{sub} (italic), _{~sub} (upright), ^{sup}, {cite:a,b},
// {hl:text to confirm}.
// ---------------------------------------------------------------------------------------------
const TOKEN = /(\*\*[^*]+\*\*|\*[^*]+\*|_\{[^}]*\}|\^\{[^}]*\}|\{cite:[^}]+\}|\{hl:[^}]+\})/g;
function runs(text, base = {}) {
  const mk = (t, extra = {}) => new TextRun({ text: t, font: FONT, size: 20, ...base, ...extra });
  return text.split(TOKEN).filter((s) => s !== "").map((tok) => {
    if (tok.startsWith("**")) return mk(tok.slice(2, -2), { bold: true });
    if (tok.startsWith("*")) return mk(tok.slice(1, -1), { italics: true });
    if (tok.startsWith("_{~")) return mk(tok.slice(3, -1), { subScript: true });
    if (tok.startsWith("_{")) return mk(tok.slice(2, -1), { subScript: true, italics: true });
    if (tok.startsWith("^{")) return mk(tok.slice(2, -1), { superScript: true });
    if (tok.startsWith("{cite:")) return mk(citeNumbers(tok.slice(6, -1).split(",").map((s) => s.trim())));
    if (tok.startsWith("{hl:")) return mk(tok.slice(4, -1), { highlight: "yellow" });
    return mk(tok);
  });
}

const body = (text) => new Paragraph({
  alignment: AlignmentType.JUSTIFIED, indent: { firstLine: 288 },
  spacing: { after: 60, line: 228 }, children: runs(text),
});
const h1 = (text) => new Paragraph({
  alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120, after: 60 },
  children: [new TextRun({ text, font: FONT, size: 20, smallCaps: true })],
});
const h2 = (text) => new Paragraph({
  alignment: AlignmentType.LEFT, keepNext: true, spacing: { before: 80, after: 40 },
  children: [new TextRun({ text, font: FONT, size: 20, italics: true })],
});
const bullet = (text) => new Paragraph({
  numbering: { reference: "bullets", level: 0 }, alignment: AlignmentType.JUSTIFIED,
  spacing: { after: 40, line: 228 }, children: runs(text),
});
const small = (text, opts = {}) => new Paragraph({
  alignment: opts.align || AlignmentType.JUSTIFIED, keepNext: opts.keepNext || false,
  spacing: { before: opts.before || 0, after: opts.after === undefined ? 120 : opts.after },
  children: runs(text, { size: 16, ...(opts.run || {}) }),
});

// ---------------------------------------------------------------------------------------------
// Display equations as native Word equations (OMML).
// ---------------------------------------------------------------------------------------------
const NS = 'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"';
const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const r = (t, upright = false) => `<m:r>${upright ? '<m:rPr><m:sty m:val="p"/></m:rPr>' : ""}<m:t>${esc(t)}</m:t></m:r>`;
const sub = (b, s) => `<m:sSub><m:e>${b}</m:e><m:sub>${s}</m:sub></m:sSub>`;
const sup = (b, s) => `<m:sSup><m:e>${b}</m:e><m:sup>${s}</m:sup></m:sSup>`;
const bar = (e) => `<m:bar><m:barPr><m:pos m:val="top"/></m:barPr><m:e>${e}</m:e></m:bar>`;
const frac = (n, d) => `<m:f><m:num>${n}</m:num><m:den>${d}</m:den></m:f>`;
const sum = (lo, hi, e) => `<m:nary><m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/></m:naryPr><m:sub>${lo}</m:sub><m:sup>${hi}</m:sup><m:e>${e}</m:e></m:nary>`;
const rad = (e) => `<m:rad><m:radPr><m:degHide m:val="1"/></m:radPr><m:deg/><m:e>${e}</m:e></m:rad>`;
const delim = (b, e, inner) => `<m:d><m:dPr><m:begChr m:val="${b}"/><m:endChr m:val="${e}"/></m:dPr><m:e>${inner}</m:e></m:d>`;
const pbar = sub(bar(r("p")), r("i"));
const pim = sub(r("p"), r("i,m"));
const EQ = {
  mean: pbar + r("=") + frac(r("1"), r("M")) + sum(r("m=1"), r("M"), pim),
  sd: sub(r("D"), r("i")) + r("=") + rad(frac(r("1"), r("M−1")) + sum(r("m=1"), r("M"), sup(delim("(", ")", pim + r("−") + pbar), r("2")))),
  set: sub(r("Γ"), r("i")) + r("=") + delim("{", "}", r("y∈") + delim("{", "}", r("0,1")) + r(":") + r("1−") + pbar + delim("(", ")", r("y")) + r("≤q")),
  cap: r("K=") + r("min", true) + delim("(", ")", delim("⌊", "⌋", r("cN")) + r(",") + sub(r("N"), r("single", true))),
};
let eqNo = 0;
function equation(key) {
  eqNo += 1;
  return new Paragraph({
    tabStops: [{ type: TabStopType.CENTER, position: COL / 2 }, { type: TabStopType.RIGHT, position: COL }],
    spacing: { before: 40, after: 80 },
    children: [
      new TextRun({ text: "\t", font: FONT, size: 20 }),
      ImportedXmlComponent.fromXmlString(`<m:oMath ${NS}>${EQ[key]}</m:oMath>`).root[0],
      new TextRun({ text: `\t(${eqNo})`, font: FONT, size: 20 }),
    ],
  });
}

// ---------------------------------------------------------------------------------------------
// Three-line tables, one column wide.
// ---------------------------------------------------------------------------------------------
const NONE = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const RULE = { style: BorderStyle.SINGLE, size: 6, color: "000000" };
const THIN = { style: BorderStyle.SINGLE, size: 4, color: "000000" };
function cell(text, width, o = {}) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA }, columnSpan: o.span, verticalAlign: VerticalAlign.CENTER,
    margins: { top: 20, bottom: 20, left: 50, right: 50 },
    borders: { top: o.top || NONE, bottom: o.bottom || NONE, left: NONE, right: NONE },
    children: [new Paragraph({
      alignment: o.align || AlignmentType.LEFT, spacing: { before: 0, after: 0 }, keepNext: !!o.keepNext,
      children: runs(text, { size: 16, ...(o.run || {}) }),
    })],
  });
}
function table(widths, rows) {
  // rows: [{cells:[text|{text,span,align,run}], top, bottom, align:[...]}]
  return new Table({
    width: { size: COL, type: WidthType.DXA }, columnWidths: widths,
    borders: { top: NONE, bottom: NONE, left: NONE, right: NONE, insideHorizontal: NONE, insideVertical: NONE },
    rows: rows.map((row, index) => {
      let col = 0;
      return new TableRow({
        cantSplit: true,
        children: row.cells.map((c) => {
          const spec = typeof c === "string" ? { text: c } : c;
          const span = spec.span || 1;
          const width = widths.slice(col, col + span).reduce((a, b) => a + b, 0);
          const align = spec.align || (row.align ? row.align[col] : undefined) || (col === 0 ? AlignmentType.LEFT : AlignmentType.CENTER);
          col += span;
          return cell(spec.text, width, { span: span > 1 ? span : undefined, align, top: row.top, bottom: row.bottom, run: spec.run, keepNext: index < rows.length - 1 });
        }),
      });
    }),
  });
}
const tableCaption = (number, title) => [
  small(`TABLE ${number}`, { align: AlignmentType.CENTER, before: 120, after: 0, keepNext: true }),
  small(title, { align: AlignmentType.CENTER, after: 60, keepNext: true, run: { smallCaps: true } }),
];
const tableNote = (text) => small(text, { before: 40, after: 160, run: { size: 14 } });

function figure(file, widthIn, heightIn, caption) {
  const px = (inches) => Math.round(inches * 96);
  return [
    new Paragraph({
      alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120, after: 60 },
      children: [new ImageRun({
        type: "png", data: fs.readFileSync(path.join(ROOT, "paper", "camera-ready", file)),
        transformation: { width: px(widthIn), height: px(heightIn) },
        altText: { title: caption.slice(0, 40), description: caption, name: file },
      })],
    }),
    small(caption, { after: 160 }),
  ];
}

// ---------------------------------------------------------------------------------------------
// Content
// ---------------------------------------------------------------------------------------------
const C = AlignmentType.CENTER;
const front = [
  new Paragraph({
    alignment: C, spacing: { before: 0, after: 240 },
    children: [new TextRun({
      text: "Imputation Disagreement for Selective Prediction with Missing Clinical Data: A Two-Hospital Reliability Evaluation",
      font: FONT, size: 48,
    })],
  }),
  new Paragraph({ alignment: C, spacing: { after: 0 }, children: runs("{hl:First Author, Second Author, Third Author, Fourth Author, Fifth Author}", { size: 22 }) }),
  new Paragraph({ alignment: C, spacing: { after: 0 }, children: runs("{hl:Department, University, City, Country}", { size: 20, italics: true }) }),
  new Paragraph({ alignment: C, spacing: { after: 240 }, children: runs("{hl:corresponding.author@university.edu}", { size: 18 }) }),
];

const abstract = [
  new Paragraph({
    alignment: AlignmentType.JUSTIFIED, indent: { firstLine: 272 }, spacing: { after: 120 },
    children: [
      new TextRun({ text: "Abstract—", font: FONT, size: 18, bold: true, italics: true }),
      ...runs(
        "Multiple imputation yields several predictions for each patient with incomplete measurements, and their disagreement is an appealing signal for deciding which cases to classify automatically. We evaluated that signal in a matched design on the PhysioNet 2019 two-hospital cohort (24,095 patients, 95 with dataset-defined sepsis onset in intensive care unit hours 12–24). Confidence, missingness burden and imputation disagreement ranked the same logistic-regression predictions and the same split-conformal singleton pool at a 60% acceptance target. Three findings emerged. First, marginal coverage hid a class-specific failure: set coverage was 90.75% internally and 97.24% externally, yet no positive patient’s set contained the true label (0/8 and 0/38), because the pooled threshold admitted the positive label only above a predicted risk of 0.989. Second, at equal capacity disagreement showed no stable advantage over confidence: the selective-risk difference was +0.109 percentage points internally (95% paired bootstrap interval [0.000, +0.328]) and −0.036 externally ([−0.108, +0.036]), and every ranking fell within the range of a uniform random ranking. Third, thresholds frozen in the source hospital did not transfer: external acceptance was 89.05%, 86.09% and 41.43% for confidence, disagreement and missingness instead of 60%. The prespecified conditional-increment model could not be fitted. Class-specific coverage, paired patient dispositions, a random-ranking reference and realized acceptance exposed failure modes that aggregate coverage concealed.",
        { size: 18, bold: true }),
    ],
  }),
  new Paragraph({
    alignment: AlignmentType.JUSTIFIED, indent: { firstLine: 272 }, spacing: { after: 160 },
    children: [
      new TextRun({ text: "Index Terms—", font: FONT, size: 18, bold: true, italics: true }),
      ...runs("selective prediction, conformal prediction, multiple imputation, missing data, sepsis, reliability evaluation", { size: 18, bold: true }),
    ],
  }),
];

const intro = [
  h1("I. Introduction"),
  body("Intensive care measurements are collected asynchronously and incompletely, so a model that predicts deterioration from the first 12 hours depends on how missing values are handled. Multiple imputation represents uncertainty about missing values instead of committing to one completed dataset {cite:rubin1987multiple,vanbuuren2011mice}. A by-product is that predictions vary across plausible completions: two patients with the same mean predicted risk may differ in how sensitive that risk is to the completion. This imputation disagreement is an intuitive candidate signal for deciding which predictions are safe to act on automatically."),
  body("Selective prediction defers uncertain cases to human review {cite:chow1970optimum,geifman2017selective,mozannar2020consistent}, and conformal prediction supplies prediction sets with distribution-free marginal coverage {cite:angelopoulos2023conformal}. Recent work combines conformal sets with cost-aware deferral for clinical triage {cite:kwon2026conformal}, studies conformal validity with missing values {cite:zaffran2023conformal}, applies conformal selection to clinical imputation {cite:he2026safeimpute} and calibrates by available modality {cite:wong2026mc2}. These studies do not settle whether imputation disagreement adds anything, as a ranking signal, to two signals that are available at no cost: the model’s own confidence and the amount of missing data."),
  body("Answering that question fairly requires a matched comparison. If rankings accept different numbers of patients, or choose from different candidate pools, differences in error cannot be attributed to the signal. A rare outcome adds a second difficulty: aggregate coverage and aggregate error can look reassuring while every positive patient is handled badly. A rule tuned in one hospital may also behave differently in another."),
  body("We therefore ask three questions on a two-hospital sepsis cohort (Fig. 1). **Q1:** How does overall prediction-set coverage relate to coverage and disposition among positive patients? **Q2:** With predictions, candidate pool and number accepted held fixed, how does replacing confidence with imputation disagreement change selective risk and individual dispositions? **Q3:** How much of the source-hospital acceptance capacity is retained when the same thresholds are applied at another hospital? Our contributions are as follows."),
  bullet("**A matched evaluation protocol.** Confidence, missingness burden and imputation disagreement rank the same singleton pool under the same predictor, imputation draws, conformal threshold and acceptance count, so that differences in selective risk are attributable to the ranking alone. A uniform random ranking of the same pool serves as a reference."),
  bullet("**Patient-level failure reporting.** Class-specific coverage and paired dispositions of positive patients show that 97% aggregate coverage coexisted with exclusion of the true label for every external positive patient, and we trace this to the pooled conformal threshold."),
  bullet("**Evidence on threshold transfer.** Thresholds selected in one hospital for a 60% target accepted between 41% and 89% of patients in the other hospital, depending on the signal."),
  body("The study evaluates reliability failure modes in a low-prevalence setting. It does not claim that any ranking signal is superior, and its main result for imputation disagreement is negative."),
];

const related = [
  h1("II. Related Work"),
  h2("A. Conformal Prediction and Selective Classification"),
  body("Split conformal prediction constructs prediction sets with finite-sample marginal coverage under exchangeability {cite:angelopoulos2023conformal,vovk2005algorithmic}. Marginal coverage can be dominated by the majority class; label-conditional (Mondrian) calibration targets coverage within each class {cite:vovk2005algorithmic,sadinle2019least}, and adaptive scores aim at more uniform conditional behavior {cite:romano2020classification}. Coverage under covariate shift or other departures from exchangeability requires weighting or explicit bounds {cite:tibshirani2019covariate,barber2023beyond}. Selective classification trades coverage for risk by abstaining {cite:chow1970optimum,geifman2017selective}, and learning-to-defer methods train the deferral rule jointly with the classifier {cite:mozannar2020consistent}. Clinical triage studies have combined conformal sets with cost-aware deferral and evaluated risk at fixed acceptance levels {cite:kwon2026conformal}. Li et al. pair patient dispositions to study release-side risk under prevalence shift, using distinct target-cohort subsets for prevalence correction, calibration and evaluation {cite:li2026deployment}. Here the rankings share the source model and singleton pool, and the external evaluation applies source thresholds without target-site recalibration."),
  h2("B. Missing Data and Uncertainty"),
  body("Multiple imputation propagates uncertainty about missing values into downstream estimates {cite:rubin1987multiple,little2019statistical}, and chained-equation imputation is a standard implementation {cite:vanbuuren2011mice}. Prior work studies conformal validity with imputed covariates, primarily for regression with an extension to classification {cite:zaffran2023conformal}. SafeImpute scores candidate imputed values by predictive dispersion under graph perturbations and uses conformal selection to control the false discovery rate of released values {cite:he2026safeimpute}; other work calibrates by available modality {cite:wong2026mc2}. Evidential deep learning with spline-based imputation estimates uncertainty within a sequence model for sparse health time series {cite:vavaroutas2025squiredl}. Our unit of selection is a patient classification, and the disagreement score measures variation in that patient’s predicted risk across imputations of a shared tabular predictor."),
];

const fig1 = figure("fig_pipeline.png", 7.16, 2.05,
  "Fig. 1.  Study pipeline. (1) Hospital A is split into training, rule-selection, calibration and internal-test partitions; Hospital B is held out for external testing. (2) A chained-equation imputer produces *M* = 10 completions that a shared logistic regression scores; the mean *p̄*_{i} and the standard deviation *D*_{i} of the *M* probabilities summarize each patient. (3) Split conformal prediction (*α* = 0.10) sends singleton sets to the automatic pool and defers empty and two-label sets. (4) Confidence (B2), missingness burden (B3) and imputation disagreement (B4) rank the same pool, which is accepted at equal capacity *K* or with cutoffs frozen in Hospital A. (5) Coverage, selective risk, paired dispositions and realized acceptance are evaluated internally and externally.");

const methods = [
  h1("III. Methods"),
  h2("A. Cohort, Labels and Partitions"),
  body("We use training sets A and B of the PhysioNet/Computing in Cardiology Challenge 2019 {cite:reyna2020early,goldberger2000physiobank}, each from a different hospital system; their sepsis labels follow the Sepsis-3 definition {cite:singer2016sepsis3}. Eligible records contain intensive care unit (ICU) hours 1 through 24, and features use observations through hour 12. The challenge label turns positive six hours before the dataset-defined onset, so for records with an observed 0-to-1 transition we add six hours to the first positive label to recover the onset. We exclude records that are positive at the first observation, for which onset cannot be localized, and patients with onset by hour 12. The outcome is positive when the recovered onset falls after hour 12 and through hour 24."),
  body("Hospital A is split at the patient level into training (60%), rule selection (10%), calibration (15%) and internal test (15%), stratified by outcome. Training fits the imputer and classifier; rule selection chooses the model hyperparameter and the acceptance cutoffs; calibration determines the conformal quantile. Hospital B is held out entirely as the external test set. Seeds 2026–2030 repeat the Hospital A split with the same external patients; seed 2026 is primary."),
  h2("B. Multiple Imputation and Shared Predictor"),
  body("Each of 34 physiological and laboratory variables is represented by its most recent observed value through hour 12; age, sex as recorded in the dataset’s Gender field, and a missingness indicator for each input are added. A stochastic chained-equation imputer {cite:vanbuuren2011mice} with Bayesian ridge conditional models is fitted on the training inputs (ten iterations) and produces *M* = 10 completions of every partition. Imputed values are clipped to the training range, observed values are preserved, and variables entirely missing in training contribute their indicators only."),
  body("A single L2-regularized logistic regression on standardized inputs is trained on the *M* completed copies with weight 1/*M* per copy. Its regularization parameter is chosen from {0.1, 1, 10} by average precision on the rule-selection partition, with ties resolved toward the smaller value; a 300-tree random forest is used as a robustness check. Let *p*_{i,m} denote the predicted outcome probability of patient *i* on completion *m*. We summarize the *M* predictions by their mean and sample standard deviation,"),
  equation("mean"),
  equation("sd"),
  new Paragraph({
    alignment: AlignmentType.JUSTIFIED, spacing: { after: 60, line: 228 },
    children: runs("and call *D*_{i} the imputation disagreement. Completions are never treated as independent patients."),
  }),
  h2("C. Conformal Sets and Capacity-Constrained Acceptance"),
  body("For a candidate label *y* ∈ {0, 1}, let *p̄*_{i}(1) = *p̄*_{i} and *p̄*_{i}(0) = 1 − *p̄*_{i}. The nonconformity score is 1 − *p̄*_{i}(*y*), and the threshold *q* is the ⌈(*n* + 1)(1 − *α*)⌉-th smallest score of the true labels of the *n* calibration patients at *α* = 0.10 (infinite if the index exceeds *n*). The prediction set is"),
  equation("set"),
  body("Coverage is the fraction of patients whose true label lies in Γ_{i}, computed over all test patients, including those with empty sets. Only singleton sets enter the automatic pool, with their single label as the prediction; empty and two-label sets are deferred."),
  body("At a target acceptance fraction *c* ∈ {0.40, 0.60, 0.80}, equal-capacity (batch) allocation ranks the pool and accepts the top"),
  equation("cap"),
  body("patients, where *N* is the size of the test cohort and *N*_{~single} the size of its singleton pool. Every ranking therefore accepts the same number of patients from the same pool; ties are broken by a fixed hash of the patient identifier. In the frozen-threshold evaluation, the score and hash cutoffs that realize the target on the rule-selection partition are stored and applied unchanged to each test singleton, so realized acceptance can differ across signals and sites."),
  h2("D. Comparators"),
  body("Table I lists the strategies. B0 and B1 accept every singleton and show the pool before ranking; B2–B4 are the three ranking signals. B5 and B6 are prespecified error-risk models (L2 logistic regression, *C* = 1) fitted on the rule-selection partition to predict the base classification error at *p̄*_{i} ≥ 0.5. B6 adds *D*_{i}, and B6 minus B5 is the conditional-increment contrast. They are fitted only if the partition contains at least 20 errors and 20 correct predictions."),
  ...tableCaption("I", "Acceptance Strategies"),
  table([380, 1800, 2860], [
    { cells: ["ID", "Strategy", "Ranking score"], top: RULE, bottom: THIN, align: [AlignmentType.LEFT, AlignmentType.LEFT, AlignmentType.LEFT] },
    { cells: ["B0", "Median imputation", "none (accept all singletons)"], align: [0, AlignmentType.LEFT, AlignmentType.LEFT] },
    { cells: ["B1", "Multiple imputation mean", "none (accept all singletons)"], align: [0, AlignmentType.LEFT, AlignmentType.LEFT] },
    { cells: ["B2", "Confidence", "1 − max(*p̄*_{i}, 1 − *p̄*_{i}), ascending"], align: [0, AlignmentType.LEFT, AlignmentType.LEFT] },
    { cells: ["B3", "Missingness burden", "missing fraction of 34 variables, ascending"], align: [0, AlignmentType.LEFT, AlignmentType.LEFT] },
    { cells: ["B4", "Imputation disagreement", "*D*_{i}, ascending"], align: [0, AlignmentType.LEFT, AlignmentType.LEFT] },
    { cells: ["B5", "Error-risk model", "logistic regression on B2 and B3 scores"], align: [0, AlignmentType.LEFT, AlignmentType.LEFT] },
    { cells: ["B6", "Error-risk model with *D*_{i}", "B5 inputs plus *D*_{i}"], bottom: RULE, align: [0, AlignmentType.LEFT, AlignmentType.LEFT] },
  ]),
  small("", { after: 60 }),
  h2("E. Metrics and Uncertainty"),
  body("Acceptance is the number of accepted patients divided by all test patients. Selective risk is the number of accepted patients whose prediction is wrong divided by the number accepted. Among true positives, we count those accepted with a negative prediction (false-negative acceptances) and report them as a fraction of all positives. The primary contrast is the selective risk of B4 minus that of B2 at *c* = 0.60, in percentage points (pp)."),
  body("Intervals are percentiles of 1,000 paired patient-level bootstrap resamples of the evaluation cohort with predictor and calibration fixed. Ranking and capacity are recomputed in each equal-capacity resample, and the stored cutoffs are retained in frozen-threshold resamples. Intervals for positive-class coverage are exact binomial. As a post hoc reference, we consider drawing *K* patients uniformly without replacement from the singleton pool; the number of false-negative acceptances is then hypergeometric, and we report its expectation and central 95% range. This range describes random allocation from the observed pool and is not a significance test."),
  h2("F. Stress Tests and Sensitivity Analyses"),
  body("S0 denotes the internal test set and S4 the external hospital, both under natural missingness. S1 and S2 additionally hide 10% and 30% of the observed physiological values at test time, and S3 hides the laboratory block; masks are shared across methods, and training and calibration are unchanged. Further checks use the random forest (S0, S2), *M* = 5 and 20 (S0), *α* = 0.05 (S0, S2) and five independent test-time imputation batches, from which we compute how often a patient’s decision (accept negative, accept positive, defer) differs between two batches. The primary analysis uses seed 2026, logistic regression, *M* = 10, the first imputation batch and *α* = 0.10. Run manifests record data and split hashes, and an independent implementation recomputed the reported coverage, paired dispositions and bootstrap intervals."),
];

const R = AlignmentType.RIGHT;
const resultsA = [
  h1("IV. Results"),
  h2("A. Cohort and Base-Model Discrimination"),
  body("The source contained 40,336 records, of which 24,095 were eligible (Table II). A replay of all source records found 486 label transitions whose recovered onset fell in the target window. Of these, 102 were lost because the record did not start at ICU hour 1 and 289 because it ended before hour 24, including one whose recovered onset lay beyond the released record. The 95 retained events are 19.5% of the transitions and 0.39% of eligible patients. The primary Hospital A split contained 6,104 training, 1,018 rule-selection, 1,527 calibration and 1,525 internal-test patients, with 34, 6, 9 and 8 events."),
  ...tableCaption("II", "Cohort and Test-Set Counts"),
  table([780, 760, 740, 800, 740, 680, 540], [
    { cells: ["Hospital", "Raw records", "Raw proxies", "Included patients", "Included positives", "Test patients", "Test pos."], top: RULE, bottom: THIN, align: [AlignmentType.LEFT, R, R, R, R, R, R] },
    { cells: ["A", "20,336", "334", "10,174", "57", "1,525", "8"], align: [0, R, R, R, R, R, R] },
    { cells: ["B", "20,000", "152", "13,921", "38", "13,921", "38"], align: [0, R, R, R, R, R, R] },
    { cells: ["Total", "40,336", "486", "24,095", "95", "—", "—"], bottom: RULE, align: [0, R, R, R, R, R, R] },
  ]),
  tableNote("Raw proxies are observable label transitions that place the recovered onset in the target window, before eligibility filtering."),
  body("The selected logistic regression (*C* = 0.1) reached an AUROC of 0.793 internally (95% interval [0.579, 0.947]) and 0.502 externally ([0.407, 0.596]). Average precision was 0.029 and 0.0029 against prevalences of 0.52% and 0.27%. The random-forest diagnostic reached an external AUROC of 0.581 ([0.480, 0.674]). Discrimination was therefore moderate but imprecisely estimated in the source hospital and close to chance in the external hospital."),
  h2("B. Marginal Coverage Hid the Loss of Every Positive"),
  body("Overall set coverage was 1,384/1,525 (90.75%) internally and 13,537/13,921 (97.24%) externally, at or above the nominal 90%. Positive-class coverage was 0/8 and 0/38 (Fig. 2a). The mechanism is simple. With 9 positives among 1,527 calibration patients, the pooled threshold was *q* = 0.011, so the negative label entered a set whenever *p̄*_{i} ≤ 0.011 and the positive label only when *p̄*_{i} ≥ 0.989. Predicted risks were nowhere near that level: the largest *p̄*_{i} among test positives was 0.023 internally and 0.0075 externally. Four internal positives exceeded 0.011 and received empty sets; the other four, and all 38 external positives, became negative singletons and entered the automatic pool."),
  body("No positive singleton occurred, so in every evaluated setting all accepted predictions were negative. Selective risk therefore equals the false-negative rate among accepted patients, and automatic acceptance acted as rule-out triage. Accepting every singleton (B1) would have released 1,388 internal patients including 4 of the 8 positives, and 13,575 external patients (97.51%) including all 38 positives (Table III)."),
];

const fig2 = figure("fig1_reliability.png", 7.16, 2.2,
  "Fig. 2.  Prediction-set coverage and patient disposition (logistic regression, seed 2026, *M* = 10, *α* = 0.10, 60% target). (a) Coverage of the original conformal sets among all test patients and among true positives; whiskers are exact 95% binomial intervals and the dashed line marks the nominal 90%. (b) Accepted patients as a share of the test cohort under equal-capacity allocation and under thresholds frozen in the source hospital; the dashed line marks the 60% target. (c) Positives accepted as negative predictions; grey bands show the central 95% range, and ticks the expectation, for a uniform random ranking of the same singleton pool at equal capacity. Equal-capacity B4 − B2 selective-risk differences were +0.109 pp [0.000, +0.328] internally and −0.036 pp [−0.108, +0.036] externally.");

const group = (text) => ({ cells: [{ text, span: 5, align: AlignmentType.LEFT, run: { italics: true } }] });
const resultsB = [
  h2("C. Equal-Capacity Ranking and Paired Dispositions"),
  body("At the 60% target, each ranking accepted 915 internal and 8,352 external patients (Table III). Internally, confidence accepted one positive as negative and disagreement two, a selective-risk difference of +0.109 pp (95% paired bootstrap interval [0.000, +0.328]); missingness also accepted two. Externally, confidence and missingness each accepted 24 of the 38 positives and disagreement 21, a difference of −0.036 pp ([−0.108, +0.036]). A uniform random ranking of the same pools would accept 2.64 and 23.38 positives on average, with central 95% ranges of 1–4 and 17–29, and all three rankings fell inside these ranges at both hospitals (Fig. 2c)."),
  ...tableCaption("III", "Acceptance and False-Negative Acceptances at the 60% Target"),
  table([1500, 700, 1070, 700, 1070], [
    { cells: ["", { text: "Internal (S0)", span: 2 }, { text: "External (S4)", span: 2 }], top: RULE },
    { cells: ["Strategy", "Acc. (%)", "Missed", "Acc. (%)", "Missed"], bottom: THIN },
    group("Without ranking"),
    { cells: ["B1 All singletons", "91.02", "4/8", "97.51", "38/38"] },
    group("Equal capacity (K = 915 and 8,352)"),
    { cells: ["B2 Confidence", "60.00", "1/8", "60.00", "24/38"] },
    { cells: ["B3 Missingness", "60.00", "2/8", "60.00", "24/38"] },
    { cells: ["B4 Disagreement", "60.00", "2/8", "60.00", "21/38"] },
    { cells: ["Random ranking", "60.00", "2.64 (1–4)", "60.00", "23.38 (17–29)"] },
    group("Thresholds frozen in Hospital A"),
    { cells: ["B2 Confidence", "60.26", "1/8", "89.05", "33/38"] },
    { cells: ["B3 Missingness", "60.00", "2/8", "41.43", "19/38"] },
    { cells: ["B4 Disagreement", "60.85", "2/8", "86.09", "34/38"], bottom: RULE },
  ]),
  tableNote("Acc.: accepted share of the test cohort. Missed: positives accepted as negative. Random ranking: expectation (central 95% range) for *K* uniform draws from the pool."),
  body("The external net reduction of three false-negative acceptances was not a uniform improvement. Relative to confidence, disagreement deferred six positives and newly accepted three others, while 18 positives were accepted as negative by both rankings (Table IV). The rule-selection partition contained six classification errors and 1,012 correct classifications, below the minimum of 20 errors, so B5 and B6 could not be fitted. The prespecified conditional increment of disagreement beyond confidence and missingness is therefore not estimable."),
  ...tableCaption("IV", "Paired Dispositions of Positive Patients at Equal Capacity"),
  table([1090, 740, 880, 880, 740, 710], [
    { cells: ["Test cohort", "Both miss", "B2-only miss", "B4-only miss", "Both defer", "Positives"], top: RULE, bottom: THIN },
    { cells: ["Internal", "1", "0", "1", "6", "8"] },
    { cells: ["External", "18", "6", "3", "11", "38"], bottom: RULE },
  ]),
  tableNote("A miss is an accepted negative prediction. B2: confidence; B4: imputation disagreement."),
  h2("D. Threshold Transfer"),
  body("Applied to the internal test set, the frozen cutoffs accepted 60.26% (confidence), 60.00% (missingness) and 60.85% (disagreement) of patients, close to the target. Applied to the external hospital, the same cutoffs accepted 89.05%, 41.43% and 86.09% (Fig. 2b, Table III). The confidence and disagreement rules thereby released 33 and 34 of the 38 external positives, more than at equal capacity, whereas the missingness rule released 19 while accepting far fewer patients than intended. Across the five source splits, external acceptance ranged from 79.48% to 89.54% for confidence and from 72.33% to 86.29% for disagreement, above the target in every split."),
  h2("E. Sensitivity and Stability"),
  body("Across the five seeds, the equal-capacity difference between disagreement and confidence ranged from −0.109 to +0.109 pp internally and from −0.048 to +0.012 pp externally, and it was zero for every seed under 30% additional masking (S2). In the prespecified checks it ranged from 0.000 to +0.219 pp, and every 95% interval reached zero (Table V). The disagreement ranking was also the least reproducible: between pairs of test-time imputation batches, the decision changed for 17.18% of patients on average under disagreement, compared with 4.79% under confidence and 0.79% under missingness."),
  ...tableCaption("V", "Sensitivity of the Equal-Capacity Difference (B4 − B2)"),
  table([1500, 900, 1100, 1540], [
    { cells: ["Setting", "Scenario", "Difference (pp)", "95% interval (pp)"], top: RULE, bottom: THIN },
    { cells: ["Random forest", "S0", "+0.219", "[−0.219, +0.656]"] },
    { cells: ["Random forest", "S2", "+0.219", "[0.000, +0.546]"] },
    { cells: ["*M* = 5", "S0", "+0.109", "[0.000, +0.328]"] },
    { cells: ["*M* = 20", "S0", "0.000", "[0.000, 0.000]"] },
    { cells: ["*α* = 0.05", "S0", "+0.219", "[0.000, +0.546]"] },
    { cells: ["*α* = 0.05", "S2", "0.000", "[0.000, 0.000]"], bottom: RULE },
  ]),
  tableNote("Primary setting (logistic regression, *M* = 10, *α* = 0.10, S0): +0.109 pp [0.000, +0.328]."),
];

const discussion = [
  h1("V. Discussion"),
  body("High aggregate coverage coexisted with exclusion of the true label from every positive patient’s prediction set. Split conformal coverage is a marginal guarantee under exchangeability; when positives are 0.3–0.6% of the cohort, it can be met by covering negatives alone, and here it was. The consequence for selective prediction is easy to miss: the candidate pool consisted entirely of negative predictions, so every ranking signal was choosing which rule-outs to release, not which predictions to trust."),
  body("Label-conditional (Mondrian) calibration is the natural remedy, because it sets a separate threshold for each label {cite:vovk2005algorithmic,sadinle2019least}. Here it faces a sample-size constraint: the calibration partition held nine positives, so at *α* = 0.10 the positive-class threshold would equal the lowest predicted risk among them. With limited discrimination, such a threshold would add the positive label to many negative patients’ sets, shrink the singleton pool and vary across splits. We did not evaluate class-conditional calibration; a credible assessment would need substantially more calibration events."),
  body("At equal capacity, disagreement and confidence changed which patients were accepted but not, in any stable way, how many positives were missed. The differences amount to one patient internally and three externally, their direction differed between hospitals and across splits, and none of the three signals fell outside the range expected from ranking the pool at random. With an external AUROC of 0.502, the external comparison contrasts orderings of a predictor that barely separates outcomes; we read it as evidence about failure under transfer, not about the relative quality of the signals. Disagreement also depended on the particular imputation draws, changing the decision of about one patient in six between batches."),
  body("Frozen cutoffs added a second transfer failure. The thresholds that met the 60% target internally accepted between 41% and 89% of external patients, so neither the review workload nor the number of released positives was controlled. Four reporting practices made these failures visible, and we recommend them for selective prediction with rare outcomes: (i) coverage by outcome class, with counts; (ii) the composition of the candidate pool, including whether any positive prediction can be accepted at all; (iii) paired dispositions of positive patients and a random-ranking reference at the same capacity; and (iv) realized acceptance when a rule is moved to another site."),
  body("The study has clear limits. Only 95 events were available, eight of them in the internal test set, so one patient moves any internal positive-class rate by 12.5 percentage points and the bootstrap has little resolution. The prespecified conditional-increment analysis could not be performed. Eligibility required 24 hours of recorded follow-up, which removed about four fifths of the target-window transitions and selects a subset of ICU stays, and the endpoint relies on the dataset’s onset definition and a fixed label offset. One retrospective dataset and one held-out hospital were reused across splits. Artificial masks probe sensitivity to measurement availability and are not models of missingness mechanisms. The paired disposition summaries and the random reference were added after inspection of the primary results. We evaluated neither class-conditional calibration nor a stronger base model, and conclusions about clinical workflow would require prospective data with sufficient events."),
  h1("VI. Conclusion"),
  body("In a matched two-hospital evaluation, ranking conformal singletons by imputation disagreement gave no stable reduction in selective risk relative to confidence, and no signal fell outside the range of a random ranking of the same pool. Marginal coverage of 91–97% concealed zero coverage of positive patients, and thresholds frozen in the source hospital accepted 41–89% of external patients instead of 60%. For rare outcomes, class-specific coverage, pool composition, paired dispositions and realized acceptance should be reported alongside aggregate coverage and risk before a selective-prediction rule is considered reliable."),
  h1("Data Availability and Ethics"),
  body("The PhysioNet/Computing in Cardiology Challenge 2019 data are publicly available from PhysioNet (https://physionet.org/content/challenge-2019/1.0.0/). We do not redistribute patient-level records or derived patient-level files. Aggregate result tables, figure source data and the analysis code needed to reproduce the cohort, partitions and results from the public source are available from the authors {hl:[confirm: public repository or on request]}. This retrospective secondary analysis of a public, de-identified dataset involved no patient contact or new data collection, so additional ethical approval was not required {hl:[confirm against institutional policy]}."),
  h1("Acknowledgment"),
  body("{hl:[Authors to confirm tools and scope:]} Generative AI tools (OpenAI Codex and Anthropic Claude) assisted with code review, cross-checking numeric statements against the experiment records, figure preparation and language editing. The authors reviewed all content and take full responsibility for it. {hl:[Add funding information, if any.]}"),
];

function references() {
  const missing = Object.keys(REFS).filter((k) => !citeOrder.includes(k));
  if (missing.length) throw new Error(`Uncited references: ${missing.join(", ")}`);
  return [
    h1("References"),
    ...citeOrder.map((key, i) => new Paragraph({
      alignment: AlignmentType.JUSTIFIED, indent: { left: 360, hanging: 360 }, spacing: { after: 40 },
      tabStops: [{ type: TabStopType.LEFT, position: 360 }],
      children: runs(`[${i + 1}]\t${REFS[key]}`, { size: 16 }),
    })),
  ];
}

const one = (children) => ({ properties: { type: SectionType.CONTINUOUS, page: PAGE }, children });
const two = (children) => ({
  properties: { type: SectionType.CONTINUOUS, page: PAGE, column: { count: 2, space: 360, equalWidth: true } },
  children,
});
const tail = [...resultsB, ...discussion];
const doc = new Document({
  creator: "Author group",
  title: "Imputation Disagreement for Selective Prediction with Missing Clinical Data",
  description: "Integrated manuscript draft for IEEE BDDM 2026 (Workshop 3)",
  styles: { default: { document: { run: { font: FONT, size: 20 } } } },
  hyphenation: { autoHyphenation: true, consecutiveHyphenLimit: 2, doNotHyphenateCaps: true },
  numbering: {
    config: [{
      reference: "bullets",
      levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 360, hanging: 200 } } } }],
    }],
  },
  sections: [
    { properties: { page: PAGE }, children: front },
    two([...abstract, ...intro, ...related]),
    one(fig1),
    two([...methods, ...resultsA]),
    one(fig2),
    two([...tail, ...references()]),
  ],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, buffer);
  console.log(`Wrote ${OUT} (${citeOrder.length} references, ${eqNo} equations)`);
});
