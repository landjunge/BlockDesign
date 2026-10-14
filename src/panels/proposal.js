import { tint } from '../core/palette.js';
import { t } from '../i18n.js';
export function proposalCard(proposal, store, retained = false, projects = null) {
  const s = store.getState(),
    lang = s.ui.language;
  const card = document.createElement('article');
  card.className = 'proposal-card';
  card.dataset.proposalId = proposal.id;
  const title = document.createElement('h3');
  title.textContent = proposal.title;
  const sample = document.createElement('div');
  sample.className = 'proposal-sample';
  sample.textContent = proposal.changes.label || proposal.title;
  Object.assign(sample.style, {
    background: tint(proposal.changes.color || '#ffffff', proposal.changes.brightness || 0),
    color: proposal.changes.font?.color || '#000000',
    borderRadius: `${proposal.changes.radius || 0}px`,
    fontFamily: proposal.changes.font?.family || 'system-ui',
    fontSize: `${proposal.changes.font?.size || 14}px`,
    border: `${proposal.changes.borderWidth ?? 1}px solid ${proposal.changes.borderColor || '#808080'}`,
  });
  const actions = document.createElement('div');
  actions.className = 'np-actions';
  const apply = document.createElement('button');
  apply.type = 'button';
  apply.className = 'np-button';
  apply.dataset.action = 'apply';
  apply.textContent = t(lang, 'apply');
  apply.disabled = !s.selection.length || !!s.ui.preview || !!s.ui.grabbed;
  apply.addEventListener('click', async () => {
    try {
      const action = {
        type: 'proposalApply',
        changes: proposal.changes,
        sourceTask: proposal.source_task,
        proposalId: proposal.id,
      };
      const result = projects
        ? await projects.apply(action, {
            source_task: proposal.source_task,
            proposal_id: proposal.id,
            pre_snapshot:
              store.getState().tasks.find((t) => t.task_id === proposal.source_task)
                ?.pre_snapshot || null,
          })
        : store.dispatch(action);
      if (result.ok !== false) store.dispatch({ type: 'notice', message: 'changed' });
    } catch (e) {
      store.dispatch({ type: 'notice', message: e.message, error: true });
    }
  });
  actions.append(apply);
  if (!retained) {
    const retain = document.createElement('button');
    retain.type = 'button';
    retain.className = 'np-button';
    retain.dataset.action = 'retain';
    const exists = s.myspace.some((p) => p.id === proposal.id);
    retain.textContent = t(lang, exists ? 'retained' : 'retain');
    retain.disabled = exists;
    retain.addEventListener('click', async () => {
      try {
        if (projects)
          await projects.apply(
            { type: 'retain', proposal },
            {
              source_task: proposal.source_task,
              proposal_id: proposal.id,
              pre_snapshot:
                store.getState().tasks.find((t) => t.task_id === proposal.source_task)
                  ?.pre_snapshot || null,
            },
          );
        else store.dispatch({ type: 'retain', proposal });
      } catch (e) {
        store.dispatch({ type: 'notice', message: e.message, error: true });
      }
    });
    actions.append(retain);
  }
  const description = document.createElement('p');
  description.textContent = proposal.description || '';
  card.append(title, sample, description, actions);
  return card;
}

export function changeSummary(actions, state) {
  const lang = state.ui.language;
  const labels = {
    x: 'X',
    y: 'Y',
    width: t(lang, 'width'),
    height: t(lang, 'height'),
    label: t(lang, 'label'),
    type: t(lang, 'type'),
    color: t(lang, 'color'),
    paletteIndex: t(lang, 'color'),
    brightness: t(lang, 'brightness'),
    radius: lang === 'de' ? 'Rundung' : 'Corner radius',
    borderColor: lang === 'de' ? 'Rahmenfarbe' : 'Border colour',
    borderWidth: lang === 'de' ? 'Rahmenbreite' : 'Border width',
    family: lang === 'de' ? 'Schriftfamilie' : 'Font family',
    size: lang === 'de' ? 'Schriftgröße' : 'Font size',
  };
  const value = (v) =>
    typeof v === 'number'
      ? new Intl.NumberFormat(lang, { maximumFractionDigits: 4 }).format(v)
      : String(v ?? '—');
  return actions
    .map((op) => {
      if (op.type === 'grid')
        return `${t(lang, 'grid')}: ${value(state.grid.spacing)} → ${value(op.spacing)} px · ${lang === 'de' ? 'Fangbereich' : 'Snap'} ${value(state.grid.magnet)} → ${value(op.magnet)} px`;
      const box = state.boxes.find((b) => b.id === op.box_id),
        title = `Box ${box?.number || '?'}`;
      if (op.type === 'scale')
        return `${title} · ${lang === 'de' ? 'Skalieren' : 'Scale'} × ${value(op.factor)}`;
      return (
        title +
        '\n' +
        Object.entries(op.changes)
          .flatMap(([key, v]) =>
            key === 'font'
              ? Object.entries(v).map(
                  ([k, n]) =>
                    `  ${labels[k] || t(lang, 'color')}: ${value(box?.font?.[k])} → ${value(n)}`,
                )
              : [`  ${labels[key] || key}: ${value(box?.[key])} → ${value(v)}`],
          )
          .join('\n')
      );
    })
    .join('\n\n');
}
