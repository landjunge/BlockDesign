import { t } from '../i18n.js';
export function mountLayersGrid(store, root) {
  root.querySelectorAll('[data-layer]').forEach(el => el.addEventListener('click', () => store.dispatch({ type: 'layer', layer: Number(el.dataset.layer) })));
  root.querySelectorAll('[data-view]').forEach(el => el.addEventListener('click', () => store.dispatch({ type: 'view', view: el.dataset.view })));
  root.querySelector('#zoom').addEventListener('change', e => store.dispatch({ type: 'zoom', zoom: Number(e.target.value) }));
  root.querySelector('#grid-toggle').addEventListener('click', () => store.dispatch({ type: 'gridToggle' }));
  root.querySelector('#refine').addEventListener('click', () => { const { grid } = store.getState(); store.dispatch({ type: 'grid', spacing: grid.spacing / 2, magnet: grid.magnet / 2 }); });
  root.querySelector('#coarsen').addEventListener('click',()=>{const {grid}=store.getState();store.dispatch({type:'grid',spacing:grid.spacing*2,magnet:grid.magnet*2});});
  store.subscribe(s => {
    root.querySelectorAll('[data-layer]').forEach(el => { el.setAttribute('aria-pressed', String(Number(el.dataset.layer) === s.activeLayer)); el.title = `${t(s.ui.language, 'layer')} ${el.dataset.layer}`; });
    root.querySelectorAll('[data-view]').forEach(el => el.setAttribute('aria-pressed', String(el.dataset.view === s.ui.view)));
    root.querySelector('#zoom').value = s.ui.zoom;
    root.querySelector('#grid-toggle').setAttribute('aria-pressed', String(s.grid.enabled));
    const format=n=>new Intl.NumberFormat(s.ui.language,{maximumFractionDigits:6}).format(n);
    root.querySelector('#grid-info').textContent = `${format(s.grid.spacing)} px`;
    root.querySelector('#grid-info').title=t(s.ui.language,'gridInfo',{spacing:format(s.grid.spacing),magnet:format(s.grid.magnet)});
    root.querySelector('#refine').disabled=s.grid.spacing/2<.25;root.querySelector('#coarsen').disabled=s.grid.spacing*2>1000;
  });
}
