import { t } from '../i18n.js';
import { proposalCard } from './proposal.js';
export function mountMyspace(store, root, projects) {
  const retained = root.querySelector('#retained');
  store.subscribe(s => {
    retained.replaceChildren();
    if (!s.myspace.length) { const p = document.createElement('p'); p.className = 'np-meta'; p.textContent = t(s.ui.language, 'emptyMy'); retained.append(p); }
    for (const proposal of s.myspace) retained.append(proposalCard(proposal, store, true,projects));
  });
}
