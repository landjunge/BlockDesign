import { tint } from '../core/palette.js';
import { t } from '../i18n.js';
export function proposalCard(proposal, store, retained = false) {
  const s = store.getState(), lang = s.ui.language;
  const card = document.createElement('article'); card.className = 'proposal-card'; card.dataset.proposalId = proposal.id;
  const title = document.createElement('h3'); title.textContent = proposal.title;
  const sample = document.createElement('div'); sample.className = 'proposal-sample'; sample.textContent = proposal.changes.label || proposal.title;
  Object.assign(sample.style, { background: tint(proposal.changes.color || '#ffffff', proposal.changes.brightness || 0),
    color: proposal.changes.font?.color || '#000000', borderRadius: `${proposal.changes.radius || 0}px`,
    fontFamily: proposal.changes.font?.family || 'system-ui', fontSize: `${proposal.changes.font?.size || 14}px`,
    border: `${proposal.changes.borderWidth ?? 1}px solid ${proposal.changes.borderColor || '#808080'}` });
  const actions = document.createElement('div'); actions.className = 'np-actions';
  const apply = document.createElement('button'); apply.type = 'button'; apply.className = 'np-button'; apply.dataset.action = 'apply'; apply.textContent = t(lang, 'apply');
  apply.disabled = !s.selection.length || !!s.ui.preview || !!s.ui.grabbed;
  apply.addEventListener('click', () => store.dispatch({ type: 'proposalApply', changes: proposal.changes }));
  actions.append(apply);
  if (!retained) {
    const retain = document.createElement('button'); retain.type = 'button'; retain.className = 'np-button'; retain.dataset.action = 'retain';
    const exists = s.myspace.some(p => p.id === proposal.id); retain.textContent = t(lang, exists ? 'retained' : 'retain'); retain.disabled = exists;
    retain.addEventListener('click', () => store.dispatch({ type: 'retain', proposal })); actions.append(retain);
  }
  const description = document.createElement('p'); description.textContent = proposal.description || '';
  card.append(title, sample, description, actions); return card;
}
