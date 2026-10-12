---
name: wechat-editorial-review
description: Review Chinese WeChat long-form articles before publication for thesis and structure, factual and citation integrity, technical or product accuracy, causal and statistical reasoning, prose and author voice, visuals, mobile readability, and publishing completeness. Use for 审稿、校稿、事实核查、技术文章审核、公众号发布前检查、压缩长文或逐条修改建议. Default to a read-only review; do not rewrite, publish, or operate a live publishing backend unless the user explicitly asks.
---

# WeChat Editorial Review

Produce a defensible publication decision, not a generic list of writing tips. Protect the author's point of view while separating facts, inference, examples, and rhetoric.

## Establish scope

1. Read the full article before judging individual lines.
2. Read repository instructions and any project-specific writing or WeChat formatting skill. Treat those local rules as authoritative for house style and rendering.
3. Determine the requested mode:
   - **Review:** findings only. This is the default.
   - **Review and revise:** report material issues, then edit the article.
   - **Pre-publish check:** emphasize assets, rendering, title, digest, references, and platform constraints.
4. Use the local source file as the review authority when a private publishing page cannot be read. State what was and was not inspected.
5. Do not infer permission to publish, upload, install software, or change a live backend from a request to review.

## Route to the relevant guidance

- For facts, quotations, dates, metrics, vendor claims, and citations, read [references/fact-checking.md](references/fact-checking.md).
- For experiments, growth metrics, causal claims, holdouts, significance, or ROI, read [references/causal-statistical-review.md](references/causal-statistical-review.md).
- For line editing, Chinese typography, author voice, repetition, and AI-polish patterns, read [references/copy-editing.md](references/copy-editing.md).
- For images, tables, HTML/mobile review, cover, digest, and WeChat handoff, read [references/wechat-publishing.md](references/wechat-publishing.md).
- For the external skills consulted when this skill was created, see [references/provenance.md](references/provenance.md).

Load only the references needed for the current review.

## Review workflow

### 1. Run deterministic preflight

When a local Markdown article is available, run:

```bash
python3 <skill-dir>/scripts/audit_article.py <article.md>
```

Use `--json` when another tool will consume the result. The script is diagnostic only; confirm findings in the article before reporting them.

### 2. Map the argument

Write a private one-sentence thesis and a short chain of supporting claims. Check:

- Does the opening promise the article actually delivered?
- Does each section answer the next likely reader question?
- Is a mechanism demonstrated, or merely asserted?
- Does a counterargument change the conclusion or only decorate it?
- Which sections repeat the same conceptual move?

Do not recommend cuts solely because the article is long. Name the repeated function and the information that would remain after the cut.

### 3. Build a claim ledger

Extract the claims that could change the reader's belief or decision. Prioritize:

- product capabilities and architecture;
- customer outcomes, dates, durations, costs, and percentages;
- causal statements;
- superlatives and universal claims;
- attributed quotations;
- claims used in the title, opening, charts, or conclusion.

Label each as fact, inference, illustrative example, opinion, or internal claim. Verify the highest-impact claims first. Prefer primary sources, open every cited source, record the relevant date and scope, and distinguish vendor positioning from independent outcome evidence.

### 4. Review methods and causality

For experiment or growth writing, test whether the proposed evidence can support the conclusion. Look for selection bias, missing counterfactuals, interference between groups, underpowered cells, post-treatment segmentation, metric-definition drift, and claims that significance follows from sample size alone.

Treat formulas, thresholds, sample sizes, and effect sizes as real claims unless the article clearly labels them as illustrative.

### 5. Review technical fidelity

Compare technical explanations with current primary documentation. Separate:

- official product vocabulary;
- the author's explanatory model;
- implementation advice;
- observed customer outcomes;
- speculation about competitive advantage.

An explanatory framework may differ from vendor terminology, but the article must label the difference where a reader could mistake it for an official architecture.

### 6. Line-edit without replacing the author

Preserve the strongest existing qualities: cadence, directness, humor, technical density, and characteristic metaphors. Flag only changes that improve reader comprehension, factual precision, consistency, or platform fit.

Identify clusters of absolute language, slogan-like contrasts, excessive em dashes, repeated section-ending aphorisms, abstract noun stacks, terminology drift, and paragraphs that sound more polished than informative. Do not ban a device mechanically; explain the reader-facing cost.

### 7. Check visuals and mobile rendering

Verify every referenced asset exists and every visual makes the intended relationship legible without relying on the caption. Check table width, long code blocks, formulas, paragraph density, image captions, title hierarchy, and placeholder text.

When browser automation is available, inspect the rendered article at a narrow mobile viewport and capture evidence. If it is not available, explicitly mark mobile rendering as unverified rather than guessing.

### 8. Check publishing completeness

Confirm title, digest, cover, body headline, figure numbering, references, original-content declaration, and manual image-upload steps are consistent. Treat missing cover art, missing body images, broken rendering, or a title mismatch as publication blockers.

## Severity and verdict

- **P0 — blocks publication:** central falsehood, unsupported core claim, material privacy/legal risk, missing required asset, broken render, or a conclusion the evidence cannot support.
- **P1 — must fix:** important overstatement, causal or statistical flaw, misleading framing, title/digest mismatch, unmarked illustrative number, or serious mobile readability issue.
- **P2 — should improve:** repetition, weak transition, terminology drift, tonal inconsistency, avoidable jargon, or local clarity problem.
- **P3 — optional polish:** preference-level wording or formatting with no material reader impact.

Choose one verdict:

- **Do not publish yet** — at least one unresolved P0.
- **Publish after revisions** — no P0, but material P1 findings remain.
- **Ready to publish** — no material P0 or P1 findings; explicitly list any unverified surface.

## Report format

Lead with the verdict and the two or three reasons that determine it. Then provide:

1. **What already works** — no more than three concrete strengths.
2. **Findings** — ordered P0 → P2 and then by article position. Each finding includes location, short quotation, problem, consequence, evidence, and smallest credible fix.
3. **Claim ledger** — claim, type, verdict, confidence, source or required action.
4. **Structural edits** — cuts, moves, or additions with the argument function preserved.
5. **Publishing checklist** — assets, title/digest, references, render, mobile, manual steps.
6. **Unresolved** — what could not be verified and what evidence would resolve it.

Avoid rewriting the whole article inside the review. If the user asks for edits, make the smallest safe changes after presenting or recording the material findings, then rerun preflight and the relevant checks.
