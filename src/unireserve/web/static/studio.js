/* CR-003: synchronously update both the color AND label for live-status badges. */
(() => {
  const states = {
    AVAILABLE: {label:'Available', color:'available'},
    SOON: {label:'Starting soon', color:'soon'},
    OCCUPIED: {label:'Booked now', color:'occupied'},
    CLOSED: {label:'Closed hours', color:'closed'},
    DISABLED: {label:'Unavailable', color:'disabled'}
  };
  const colors = Object.values(states).map(s => s.color);
  function apply(el, name) {
    if (!states[name]) return;
    const state = states[name];
    el.dataset.state = name;
    if (el.classList.contains('aztu-seat') || el.classList.contains('map-pin')) {
      colors.forEach(color => el.classList.remove('state-' + color));
      el.classList.add('state-' + state.color);
      const title = el.querySelector('.pin-name');
      if (title) el.setAttribute('aria-label', title.textContent.trim() + ': ' + state.label);
    }
    if (el.classList.contains('signal-pill')) {
      colors.forEach(color => el.classList.remove('signal-' + color));
      el.classList.add('signal-' + state.color);
    }
    const text = el.querySelector('[data-status-text]');
    if (text) text.textContent = state.label;
  }
  async function refresh() {
    if (document.visibilityState === 'hidden') return;
    const note = document.getElementById('refresh-note');
    try {
      const response = await fetch('/api/availability-status', {
        credentials:'same-origin',cache:'no-store',headers:{Accept:'application/json'}
      });
      if (!response.ok) throw new Error('Status fetch failed');
      const result = await response.json();
      for (const el of document.querySelectorAll('[data-resource-id]')) {
        const status = result.resources?.[el.dataset.resourceId];
        if (status) apply(el, status.state);
      }
      const clock = document.getElementById('checked-at');
      if (clock) clock.textContent = result.checked_at;
      if (note) {note.textContent = 'Status updated · every 30 seconds';note.dataset.connection = 'online';}
    } catch (error) {
      if (note) {note.textContent = 'Live update paused — refresh this page to retry';note.dataset.connection = 'offline';}
    }
  }
  window.setInterval(refresh,30000);
  document.addEventListener('visibilitychange',()=>{if (document.visibilityState === 'visible') refresh();});
  for (const tab of document.querySelectorAll('[data-zone-filter]')) {
    tab.addEventListener('click',()=>{
      const chosen = tab.dataset.zoneFilter;
      for (const t of document.querySelectorAll('[data-zone-filter]')) {
        const on = t === tab;
        t.classList.toggle('selected',on);
        t.setAttribute('aria-pressed',String(on));
      }
      for (const zone of document.querySelectorAll('[data-zone-id]')) {
        zone.hidden = chosen !== 'all' && zone.dataset.zoneId !== chosen;
      }
    });
  }
})();