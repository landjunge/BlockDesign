# Design source/reference contract v1 – preparation, not active import

BD-C01/D01/R01, seven-tools-build-20261018-1833. This document defines the
next adapter boundary before BD-C02–04 implementation. It does not introduce a
new job queue, executable endpoint, HTML importer or automatic deployment.

A design descriptor extends the existing `threaddesk.handoff.v1` at
`context.design`; outer handoff/task/run identity and issuance remain governed by
ThreadDesk/KiraBridge. No second work-order format replaces those contracts.
The descriptor's own `format` is `blockdesigner.source.v1`. The prepared
[JSON Schema](design-source-v1.schema.json) fixes shape/limits, not implementation.
The initial proposal carries an inert PNG preview only; requested_style is
bounded untrusted descriptive text, never executable CSS/code. Semantic checks
(unique box IDs, exact source-element hash, unresolved→question) remain mandatory
in the future adapter; structural schema validity alone never authorizes dispatch.

| Field | Meaning / Bedeutung |
|---|---|
| `project_id`, `snapshot_id` | Existing saved BlockDesigner project and immutable source snapshot |
| `document_revision` | Exact monotone editor revision; separate from ThreadDesk/handoff revision |
| `document_size` | Existing editor document width/height in document pixels (currently1000×640) |
| `source.artifact_sha256` | SHA256 of the actual supplied original HTML/image artifact; no invented hash |
| `source.source_commit` | Optional actual source commit, null if unavailable; not inferred from filename |
| `source.media_type` | `text/html` or `image/png`; format does not prove safe execution |
| `source.reference_viewport` | Width/height at which the target page/reference was rendered; not the editor window or document size |
| `view.zoom` | Display scale only; never changes persisted document coordinates |
| `preview.artifact_sha256` | Actual inert preview image hash; the image is separate from original source |
| `elements[]` | Box-ID, `move`/`replace`/`new`, exact source element/component reference or explicit unresolved state, desired geometry/style |
| `requested_change` | Explicit user's change request; untrusted context, not execution authority by itself |

Original HTML stays immutable at import. Subsequent coding modifies original
source/components only through a separately authorized issued task. Imported
HTML may not access module, task, credentials or Bridge endpoints. The first
implementation should render an inert image or sandbox without scripts,
same-origin privileges, navigation, popups or network; a preview is never trusted
control UI. Sanitization/sandbox and artifact verification require their own
BD-C02 implementation and adversarial tests before being advertised as available.

An element reference carries the bound source-artifact hash plus an exact
selector/component ID and `resolution:unique`. Two similar buttons are not the
same element. Unknown/ambiguous references use `resolution:unresolved` and cause
a concrete question before an existing element is moved/replaced. A `new` box has
no claimed original element. No image-similarity confidence becomes proof.
Actions preserve box identity/number/orientation/layer and existing grouping.
Style edits do not implicitly discard bound event handlers/backend dependencies.

Source artifact/commit, target reference viewport, editor document size, editor
window size and display zoom are five separate concepts. The editor's existing
1180×760 minimum working window/1440×900 reference does not prescribe target-page
responsive breakpoints or mobile stacking. Those target relationships must be
explicit in each design request; no new global responsive rule is introduced.

Before dispatch, bind project/snapshot/documentrevision/sourcehash/selection to
the existing issued handoff. A changed source/revision is conflict, not a silent
refresh. Same request identity repeats the existing task; uncertain delivery
reads it. Delivery/preview remains unverified until actual checks and explicit
user decision. A later preview cannot overwrite a newer design. Missing source,
commit, element mapping or image-consumption capability remains unknown.

Current code has box model1, project/body format1, monotone revisions,
existing Whiteboard task/snapshot/reply binding and preview decision. It does
**not** yet persist/validate `context.design`, import HTML, map DOM elements or
expose this via MCP. BD-C02–04 implement those pieces against this boundary;
KiraBridge integration remains with the coordinator. See architecture.md for
existing interfaces and README.md for the current actual start path.
