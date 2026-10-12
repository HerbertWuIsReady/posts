# WeChat pre-publish review

Use this reference for a final handoff or when the repository produces WeChat-ready HTML.

## Source and metadata

- Title in front matter, rendered body, publishing backend, cover, and user-approved title must match.
- Digest should fit the platform limit and add information rather than repeat the title.
- Verify author/date/status fields when the project uses them.
- Confirm the article's opening delivers the promise made by the title and digest.

## Assets

- Resolve every local image path relative to the article source.
- Flag missing cover art and missing body images as blockers.
- Check figure numbers, captions, alt text, and article references for consistency.
- Confirm text inside generated images is correct and legible at phone width.
- Local HTML image placeholders may require manual upload and replacement in the WeChat editor. Do not report an image as uploaded merely because the file exists locally.

## Body and references

- Apply the project's local table-width limit; three columns is a safe default for mobile when no stricter rule exists.
- Check long code blocks, formulas, and wide tables for horizontal overflow.
- Distinguish official quotes from the author's insight styling.
- Ensure external claims retain source names and dates even when WeChat moves or suppresses links.
- Verify the reference list survived rendering.

## Render and mobile QA

Inspect the generated HTML when available. At minimum check:

- heading hierarchy and whitespace;
- paragraph density and orphaned characters;
- quote and insight boxes;
- code indentation;
- table overflow;
- image placeholder placement;
- formula rendering;
- final reference section.

Use a narrow mobile viewport when browser automation is available. Capture screenshots of the opening, a dense technical section, the widest table, each real image, and the ending. If visual inspection was not possible, mark it unverified.

## Handoff checklist

- cover uploaded;
- title and digest copied;
- body pasted from rendered output rather than raw HTML source;
- every local image manually replaced where required;
- original-content declaration reviewed;
- preview sent to a real phone;
- links, tables, code, formulas, and images checked after paste;
- final backend version compared with the reviewed local source.

Publishing is an external mutation. Perform it only when the user explicitly asks, even when the article passes review.
