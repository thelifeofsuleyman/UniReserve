/* CR-001: periodic read-only status refresh for the availability studio. */
(() => {
  const legend = {
    AVAILABLE: ['Available', 'available'],
    SOON: ['Booked soon', 'soon'],
    OCCUPIED: ['Reserved', 'occupied'],
    DISABLED: ['Disabled', 'disabled'],
  };
  async function refresh() {
    const note = document.getElementById('refresh-note');
    try {
      const response = await fetch('/api/availability-status', {
        credentials: 'same-origin', cache: 'no-store', headers: {Accept: 'application/json'}
      });
      if (!response.ok) throw new Error('Unable to refresh statuses');
      const payload = await response.json();
      for (const element of document.querySelectorAll('[data-resource-id]')) {
        const value = payload.resources[element.dataset.resourceId];
        if (!value || !legend[value.state]) continue;
        element.dataset.state = value.state;
        if (element.classList.contains('map-pin')) {
          element.classList.remove('state-available', 'state-soon', 'state-occupied', 'state-disabled');
          element.classList.add('state-' + legend[value.state][1]);
          const sub = element.querySelector('[data-status-text]');
          if (sub) sub.textContent = legend[value.state][0];
          element.setAttribute('aria-label', element.querySelector('.pin-name').textContent.trim() + ': ' + legend[value.state][0]);
        }
        const dot = element.querySelector('.signal-dot');
        if (dot) {
          dot.classList.remove('available','soon','occupied','disabled');
          dot.classList.add(legend[value.state][1]);
        }
      }
      const at = document.getElementById('checked-at');
      if (at) at.textContent = payload.checked_at;
      if (note) note.textContent = 'Status refreshed successfully';
    } catch (error) {
      if (note) note.textContent = 'Status refresh unavailable — reload to retry';
    }
  }
  window.setInterval(refresh, 30000);
})();
