# Design source/reference contract v1 – local import; handoff remains separate

BD-C01–03/D01/R01, seven-tools-build-20261018-1833. The original prepared boundary
is now used by a local inert-reference importer and static element mapping.
BD-C04 issuance/run/return integration remains with ThreadDesk/KiraBridge.
There is no new work queue, executable HTML endpoint or automatic deployment.

A design descriptor extends the existing `threaddesk.handoff.v1` at
`context.design`; outer handoff/task/run identity and issuance remain governed by
ThreadDesk/KiraBridge. No second work-order format replaces those contracts.
The descriptor's own `format` is `blockdesigner.source.v1`. The prepared
[JSON Schema](design-source-v1.schema.json) fixes the descriptor shape/limits.
The local implementation carries an inert PNG preview only; requested_style is
bounded untrusted descriptive text, never executable CSS/code. Semantic checks
(unique box IDs, exact source-element hash, unresolved→question) remain mandatory
in every later adapter; structural schema validity alone never authorizes dispatch.

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

The current importer accepts an explicitly declared reference viewport and checks
its aspect ratio against actual PNG dimensions. It does not infer a verified CSS
viewport from image pixels (e.g. HiDPI). The background is uniformly fit from0/0
with `scale=min(document.width/viewport.width, document.height/viewport.height)`;
remaining canvas space stays empty. Existing zoom is applied over that document.
Viewport declarations and the PNG/HTML relationship remain unverified claims;
the image/source SHA256 values are computed over actual immutable uploaded bytes.
`source_commit` is currently null, not a guessed Git commit.

Before dispatch, bind project/snapshot/documentrevision/sourcehash/selection to
the existing issued handoff. A changed source/revision is conflict, not a silent
refresh. Same request identity repeats the existing task; uncertain delivery
reads it. Delivery/preview remains unverified until actual checks and explicit
user decision. A later preview cannot overwrite a newer design. Missing source,
commit, element mapping or image-consumption capability remains unknown.

## Implemented local boundary

Box/project/body format1, monotone revisions and existing CAS/snapshots are
preserved. An optional document `design` stores source/preview metadata, a
bounded static-ID catalog and box bindings; old documents have no reference.
PNG/HTML bytes are deduplicated in the existing artifact store, checked by hash
on save/read/history and never silently deleted. Missing/corrupt artifacts fail
closed; recovery keeps historical data. Old Undo frames mean no background.

POST `/api/design/import` accepts bounded base64 PNG plus optional UTF-8 HTML
and reference_viewport. It only validates/parses text and publishes immutable
artifacts under existing local project storage. GET
`/api/design/preview/<sha256>` verifies and serves a PNG only. HTML has no serving,
iframe, browser parsing, script, network, task or secret interface. Existing
Host/Origin/CSP restrictions remain. PNG is RGB/RGBA8, noninterlaced/static,
max1MiB/4Megapixels; HTML max256KiB and256 ID occurrences. Arbitrary paths/URLs
are not accepted. No parser/PNG result is a functional test.

`id:<exact HTML id>` identifies an occurrence in the static source, not an
authenticated live DOM/component. Duplicate/inert-template/noscript IDs remain
unresolved; visually similar labels are not identity. Runtime-created IDs and
functionality are unverified. Box assignment uses current revision/hash and
active-layer checks; new adds no original reference. Source changes leave old
hashes stale. Viewport changes require explicit reassignment. Two boxes claiming
the same original element produce a question. Moves/replacements only describe
the desired code edit; no original pixels or code are modified here.

`describeDesign(state, project_id, snapshot_id, requested_change)` prepares the
existing descriptor and a separate read-only issues/transform wrapper.
`ready` means reference mapping is resolved only; `execution_ready:false` and
`execution_started:false` remain fixed. Stale/unresolved refs stay explicitly
unresolved in the descriptor. Project/snapshot parameters are claims until the
coordinator verifies the actual saved snapshot; no caller Boolean grants rights.
This function is **not** an issued handoff, dispatch, MCP endpoint or return.

Existing Whiteboard/Ollama box tasks are unchanged and do not receive original
HTML or the new design descriptor. Full code-agent handoff/new-preview acceptance
belongs to BD-C04 with the coordinator. See architecture.md and README.md.
