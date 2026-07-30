---
name: repo-daily-summary
description: Summarize current repository or workstream progress into concise, advisor-ready PPT bullets or a daily_summary_YYYYMMDD.md. Use for daily progress reviews, research meetings, supervisor updates, milestone summaries, or when technical repo activity must be translated for an audience that understands the field but lacks project-specific context.
---

# Repo Daily Summary

Create an evidence-based progress summary that explains the goal, material
technical progress, validated results, and next research targets.

## Workflow

1. Identify the repository root and requested workstream. Do not summarize
   unrelated subprojects.
2. If an output directory is specified, run
   `scripts/find_latest_daily_summary.py <directory>` and read the latest prior
   summary as the style and progress baseline.
3. Inspect only the evidence needed to establish the current delta:
   - recent commits and relevant working-tree changes;
   - progress, handoff, benchmark, requirements, or response documents;
   - validation reports and generated artifacts;
   - test results that materially change project status.
4. Separate evidence into:
   - **Objective**: the research or product capability being pursued;
   - **Implemented**: durable technical capabilities now present;
   - **Results**: verified outcomes or measured limitations;
   - **Next**: the shortest path to the next meaningful milestone.
5. Check every quantitative or completion claim against an artifact, test, or
   report. Distinguish a full end-to-end pass from schema-only, targeted, or
   assemble-only validation.
6. Return the summary directly unless the user requests a file. When a file is
   requested, write `daily_summary_YYYYMMDD.md` in the requested directory, or
   in the repository root when none is given.

## Audience And Style

Write for a technically literate advisor or reviewer who does not know local
case names, file paths, or internal workflow terminology.

- Lead with why the work matters, then the technical mechanism and evidence.
- Name important technologies or methods when they explain the contribution,
  such as YOLO, OCR, graph matching, SPICE, or PDK binding.
- Generalize case-specific results into capabilities. For example, prefer
  “complete visible-transistor detection on a representative paper schematic”
  over “Wang reaches 9/9.”
- Retain a number when it conveys scale or rigor, such as benchmark size,
  device count, error reduction, or coverage.
- Omit commit hashes, virtual-environment versions, directory names, and setup
  plumbing unless they are themselves the milestone.
- Avoid raw logs, implementation inventories, unexplained acronyms, and vague
  claims such as “pipeline improved.”
- State remaining limitations plainly. Do not turn partial validation into an
  end-to-end success claim.
- Use short, presentation-ready phrases rather than prose paragraphs.

## Default PPT Format

Use two slides by default. Keep each section to at most four bullets and each
bullet to one line where practical.

```markdown
### Slide 1

**<Workstream>: <Capability or Research Outcome>**

**Objective**
<one sentence>

**Implemented**
<three to four technical capability bullets>

---

### Slide 2

**<Workstream>: Validation and Next Steps**

**Results**
<three to four verified outcome bullets>

**Next**
<two to four milestone bullets>
```

If the user explicitly requests one page, keep the same sections but retain
only the highest-signal bullets. If the user requests a narrative daily report,
use the same evidence hierarchy without slide labels.

## PPTX Template

When the user requests a PowerPoint file, start from
`assets/repo-daily-summary-template.pptx`. Preserve its 16:9 master, typography,
footer placement, and page structure instead of rebuilding the design.

- **Slide 1 — weekly/multi-repo summary**: group the highest-signal work under
  major progress, supporting progress, and next priorities. Summarize
  workstreams rather than listing commits.
- **Slide 2 — reporting date**: show the week/date and presenter identity.
- **Slide 3 — single-repo summary**: use one page per repository with
  Objective, Implemented, Results, and Next.

For a multi-repo weekly deck, use slides 1 and 2, then duplicate slide 3 once
per repository. For a single-repo daily deck, use the date page and one
single-repo page; include slide 1 only when an overall summary is useful.

Replace every bracketed placeholder. Keep Objective to one sentence,
Implemented and Results to at most three bullets each, and Next to at most two
bullets. Do not shrink text to fit excessive content; remove lower-value detail
instead.

## Resources

`scripts/find_latest_daily_summary.py` prints the latest
`daily_summary_*.md` in a target directory so a new report can focus on the
delta instead of repeating unchanged background.

`assets/repo-daily-summary-template.pptx` is the canonical PowerPoint template
for weekly multi-repo and single-repo advisor updates.

`assets/report-wangchao-layout-reference.pptx` preserves the original
three-slide layout example. Use it only to audit the visual design; generate
new reports from the canonical template above.
