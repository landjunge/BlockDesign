// One registry drives both key matching and the visible help. Interaction-only
// entries describe the existing workspace/monitor handlers as well.
export const SHORTCUTS = Object.freeze([
  {
    id: 'create',
    keys: ['b'],
    key: 'B',
    de: '50 × 50 px Box erstellen',
    en: 'Create a 50 × 50 px box',
  },
  {
    id: 'layer',
    keys: ['1', '2', '3'],
    key: '1 / 2 / 3',
    de: 'Bearbeitbare Ebene wählen',
    en: 'Choose editable layer',
  },
  {
    id: 'grab',
    keys: [' '],
    key: 'Space',
    de: 'Mehrfachauswahl gemeinsam greifen/absetzen; sonst nächster Mittelpunkt',
    en: 'Grab/drop the entire multi-selection; otherwise nearest centre',
  },
  {
    id: 'height',
    keys: ['d'],
    key: 'D',
    de: 'Halten + Maus: ausschließlich Höhe',
    en: 'Hold + mouse: height only',
  },
  {
    id: 'width',
    keys: ['f'],
    key: 'F',
    de: 'Halten + Maus: ausschließlich Breite',
    en: 'Hold + mouse: width only',
  },
  { id: 'axes', key: 'D + F', de: 'Keine Größenänderung', en: 'No resizing' },
  {
    id: 'scale',
    keys: ['+', '=', '-'],
    key: '+ / −',
    de: 'Proportional × 1,1 / ÷ 1,1 skalieren',
    en: 'Scale proportionally × 1.1 / ÷ 1.1',
  },
  {
    id: 'select',
    key: 'Klick / Click',
    de: 'Box auswählen; leerer Klick leert Auswahl',
    en: 'Select a box; empty click clears selection',
  },
  {
    id: 'extend',
    key: 'Shift + Klick / Click / Enter',
    de: 'Auswahl ergänzen/entfernen; erste Box ist Primary',
    en: 'Add/remove selection; first box is Primary',
  },
  { id: 'enter', key: 'Enter', de: 'Fokussierte Box auswählen', en: 'Select focused box' },
  {
    id: 'transfer',
    keys: ['t'],
    key: 'T',
    de: 'Passende Eigenschaften von Primary übernehmen, auch Beschriftung',
    en: 'Transfer suitable Primary properties, including label',
  },
  {
    id: 'attribute',
    keys: ['a'],
    key: 'A',
    de: 'Halten, Farbe wählen, Rad: Helligkeit; Loslassen übernimmt',
    en: 'Hold, choose colour, wheel: brightness; release commits',
  },
  {
    id: 'cancel',
    keys: ['escape'],
    key: 'Escape',
    de: 'Hilfe/Historie schließen / Attributvorschau abbrechen und absetzen',
    en: 'Close help/history / cancel attribute preview and drop',
  },
  { id: 'help', keys: ['h'], key: 'H', de: 'Diese Hilfe öffnen', en: 'Open this help' },
  {
    id: 'undo',
    keys: ['z'],
    modifier: true,
    key: '⌘ / Ctrl + Z',
    de: 'Letzten Änderungsschritt rückgängig',
    en: 'Undo last change',
  },
  {
    id: 'redo',
    keys: ['y', 'z'],
    modifier: true,
    shift: true,
    key: '⌘ / Ctrl + Shift + Z · ⌘ / Ctrl + Y',
    de: 'Änderung wiederholen',
    en: 'Redo change',
  },
  {
    id: 'sidebar',
    key: '← / →',
    de: 'Bei Fokus auf Sidebar-Rand: Breite um 16 px ändern',
    en: 'With sidebar edge focused: change width by 16 px',
  },
  {
    id: 'monitor',
    key: '← ↑ ↓ →',
    de: 'Bei Fokus auf Monitor-Kopf: um 8 px verschieben',
    en: 'With monitor heading focused: move by 8 px',
  },
]);
export function matchShortcut(e) {
  const key = e.key.toLowerCase(),
    modifier = e.ctrlKey || e.metaKey;
  if (e.altKey) return null;
  if (modifier) return key === 'z' ? (e.shiftKey ? 'redo' : 'undo') : key === 'y' ? 'redo' : null;
  return SHORTCUTS.find((s) => !s.modifier && s.keys?.includes(key))?.id || null;
}
