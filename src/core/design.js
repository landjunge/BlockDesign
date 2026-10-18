// References describe a design; they never dispatch work or execute imported code.
const hash = value => typeof value === 'string' && /^[a-f0-9]{64}$/.test(value);
const plain = value => value && typeof value === 'object' && !Array.isArray(value);
const keys = (value, expected) => plain(value) && Object.keys(value).sort().join(',') === [...expected].sort().join(',');
function require(ok, code = 'designInvalidSource') { if (!ok) throw Error(code); }
export function validateDesign(design, boxes) {
  if (design == null) return;
  if (plain(design) && Number.isInteger(design.version) && design.version > 1) throw Error('storageFormat');
  require(keys(design, ['version', 'source', 'preview', 'catalog', 'bindings']) && design.version === 1);
  const source = design.source, preview = design.preview;
  require(keys(source, ['artifact_sha256', 'media_type', 'source_commit', 'reference_viewport']) && hash(source.artifact_sha256) && ['text/html', 'image/png'].includes(source.media_type) && source.source_commit === null);
  require(keys(preview, ['artifact_sha256', 'media_type', 'rendering_mode']) && hash(preview.artifact_sha256) && preview.media_type === 'image/png' && preview.rendering_mode === 'inert-image', 'designInvalidPreview');
  const view = source.reference_viewport;
  require(keys(view, ['width', 'height']) && Object.values(view).every(v => Number.isInteger(v) && v > 0 && v <= 32768), 'designInvalidPreview');
  require(Array.isArray(design.catalog) && design.catalog.length <= 256 && plain(design.bindings) && Object.keys(design.bindings).length <= 256, 'designElementLimit');
  const ids = new Set();
  for (const item of design.catalog) {
    require(keys(item, ['element_id', 'tag', 'count', 'resolution']) && typeof item.element_id === 'string' && item.element_id.length > 0 && item.element_id.length <= 259 && !ids.has(item.element_id) && typeof item.tag === 'string' && item.tag.length <= 256 && Number.isInteger(item.count) && item.count > 0 && item.count <= 256 && ['unique', 'unresolved'].includes(item.resolution));
    ids.add(item.element_id);
  }
  for (const [id, binding] of Object.entries(design.bindings)) {
    require(boxes.some(b => b.id === id) && keys(binding, ['action', 'source_element']) && ['move', 'replace', 'new'].includes(binding.action));
    const ref = binding.source_element;
    if (binding.action === 'new') require(ref === null);
    else {
      require(keys(ref, ['artifact_sha256', 'element_id', 'resolution']) && hash(ref.artifact_sha256) && (ref.element_id === null || typeof ref.element_id === 'string' && ref.element_id.length <= 512) && ['unique', 'unresolved'].includes(ref.resolution));
      if (ref.resolution === 'unique') {
        require(typeof ref.element_id === 'string' && ref.element_id.length > 0);
        if (ref.artifact_sha256 === source.artifact_sha256) require(design.catalog.some(item => item.element_id === ref.element_id && item.count === 1 && item.resolution === 'unique'), 'designForeignElement');
      }
    }
  }
}
export function bindingState(design, binding) {
  if (!binding || binding.action === 'new') return 'new';
  const ref = binding.source_element;
  if (!design || ref.artifact_sha256 !== design.source.artifact_sha256) return 'stale';
  const item = design.catalog.find(item => item.element_id === ref.element_id);
  const same = Object.values(design.bindings).filter(other => other.source_element?.artifact_sha256 === ref.artifact_sha256 && other.source_element?.element_id === ref.element_id);
  if (same.length > 1) return 'unresolved';
  return ref.resolution === 'unique' && item?.resolution === 'unique' && item.count === 1 ? 'unique' : 'unresolved';
}
export function boxBinding(design, id) {
  return design && Object.hasOwn(design.bindings, id) ? design.bindings[id] : null;
}
export function bindElement(state, action) {
  const design = state.design;
  require(design && action.expected_revision === state.revision && action.source_hash === design.source.artifact_sha256, 'designStale');
  require(['move', 'replace', 'new'].includes(action.operation));
  if (action.operation === 'new') return { action: 'new', source_element: null };
  require(action.element_id === null || typeof action.element_id === 'string');
  const item = design.catalog.find(item => item.element_id === action.element_id);
  require(action.element_id === null || item, 'designForeignElement');
  return { action: action.operation, source_element: { artifact_sha256: design.source.artifact_sha256, element_id: action.element_id, resolution: item?.count === 1 && item?.resolution === 'unique' ? 'unique' : 'unresolved' } };
}
export function sourceTransform(state) {
  const viewport = state.design.source.reference_viewport;
  return { scale: Math.min(state.document.width / viewport.width, state.document.height / viewport.height), x: 0, y: 0 };
}
export function describeDesign(state, project_id, snapshot_id, requested_change) {
  require(state.design && state.boxes.length <= 256, 'designElementLimit');
  require([project_id, snapshot_id].every(id => typeof id === 'string' && id.length > 0 && id.length <= 128));
  const issues = [];
  const elements = state.boxes.map(box => {
    require(typeof box.id === 'string' && box.id.length > 0 && box.id.length <= 128);
    const binding = boxBinding(state.design, box.id) || { action: 'new', source_element: null };
    const status = bindingState(state.design, binding);
    if (['stale', 'unresolved'].includes(status)) issues.push({ box_id: box.id, reason: status, question: 'Which exact current original element should this box change?' });
    const requested_style = JSON.stringify({ type: box.type, label: box.label, color: box.color, radius: box.radius, font: box.font, layer: box.layer });
    require(requested_style.length <= 4000, 'designElementLimit');
    const reference = structuredClone(binding);
    if (reference.source_element && status !== 'unique') reference.source_element.resolution = 'unresolved';
    return { box_id: box.id, ...reference, geometry: { x: box.x, y: box.y, width: box.width, height: box.height }, requested_style };
  });
  require(typeof requested_change === 'string' && requested_change.length > 0 && requested_change.length <= 10000);
  const descriptor = { format: 'blockdesigner.source.v1', project_id, snapshot_id, document_revision: state.revision, document_size: structuredClone(state.document), source: structuredClone(state.design.source), preview: structuredClone(state.design.preview), view: { zoom: state.ui.zoom }, elements, requested_change };
  return { descriptor, source_to_document: sourceTransform(state), ready: !issues.length, issues, execution_ready: false, execution_started: false, source_commit_verified: false, reference_viewport_verification: 'declared_not_verified', preview_source_relation: 'user_supplied_unverified', scope: 'design_description_not_handoff_or_execution' };
}
