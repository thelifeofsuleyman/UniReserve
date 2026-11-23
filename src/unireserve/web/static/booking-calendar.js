/* Reservation calendar: current booking status and future-date status are distinct. */
(() => {
  const root = document.getElementById('booking-calendar');
  if (!root) return;
  const picker = document.getElementById('calendar-date');
  const grid = document.getElementById('calendar-slots');
  const message = document.getElementById('calendar-status');
  const selection = document.getElementById('calendar-selection');
  const previous = document.getElementById('calendar-previous');
  const next = document.getElementById('calendar-next');
  const startInput = document.getElementById('start');
  const endInput = document.getElementById('end');
  const labels = {
    AVAILABLE: 'Free',
    BOOKED: 'Reserved',
    OWN_BOOKING: 'Your other booking',
    CLOSED: 'Closed',
    PAST: 'Unavailable'
  };
  let sequence = 0;
  let currentSlots = [];

  function shiftDate(iso, days) {
    // UTC midday avoids client-local timezone and daylight-saving rollover.
    const value = new Date(iso + 'T12:00:00Z');
    value.setUTCDate(value.getUTCDate() + days);
    return value.toISOString().slice(0, 10);
  }
  function updateNav() {
    previous.disabled = picker.value <= picker.min;
    next.disabled = picker.value >= picker.max;
  }
  function makeSlot(slot, index) {
    const button = document.createElement('button');
    const state = labels[slot.state] || 'Unavailable';
    button.type = 'button';
    button.className = 'booking-calendar__slot slot-' + slot.state.toLowerCase().replace('_', '-');
    button.textContent = slot.label;
    button.setAttribute('aria-label', slot.label + ', ' + state.toLowerCase());
    button.title = slot.label + '–' + slot.end.slice(11) + ' · ' + state;
    button.disabled = slot.state !== 'AVAILABLE';
    button.dataset.slotStart = slot.start;
    if (!button.disabled) {
      button.addEventListener('click', () => {
        if (!startInput || !endInput) return;
        const following = currentSlots[index + 1];
        const useHour = following && following.state === 'AVAILABLE' && following.start === slot.end;
        startInput.value = slot.start;
        endInput.value = useHour ? following.end : slot.end;
        for (const item of grid.querySelectorAll('.booking-calendar__slot')) {
          item.classList.remove('slot-selected');
        }
        button.classList.add('slot-selected');
        if (useHour) grid.children[index + 1].classList.add('slot-selected');
        selection.textContent = 'Selected ' + slot.start.slice(11) + '–' + endInput.value.slice(11)
          + '. Confirm or adjust your time below.';
      });
    }
    return button;
  }

  async function load() {
    const date = picker.value;
    if (!date || date < picker.min || date > picker.max) return;
    const id = ++sequence;
    updateNav();
    grid.replaceChildren();
    selection.textContent = '';
    message.textContent = 'Checking reservations…';
    message.dataset.connection = 'loading';
    try {
      const url = root.dataset.apiUrl + '?date=' + encodeURIComponent(date);
      const response = await fetch(url, {credentials:'same-origin', cache:'no-store',
        headers: {'Accept':'application/json'}});
      if (!response.ok) throw new Error('Unable to load the selected date');
      const data = await response.json();
      if (id !== sequence) return;
      currentSlots = data.slots || [];
      const fragment = document.createDocumentFragment();
      currentSlots.forEach((slot, index) => fragment.appendChild(makeSlot(slot, index)));
      grid.replaceChildren(fragment);
      const free = currentSlots.filter(s => s.state === 'AVAILABLE').length;
      const reserved = currentSlots.filter(s => s.state === 'BOOKED').length;
      message.textContent = free + ' free half-hour slots · ' + reserved + ' reserved'
        + (data.requires_approval ? ' · Approval required' : '');
      message.dataset.connection = 'online';
      if (!currentSlots.length) message.textContent = 'No booking hours configured for this date.';
      // Preserve the previously selected form times when navigating the calendar.
      // Checking a slot is read-only; booking is always validated on submit.
    } catch (_error) {
      if (id !== sequence) return;
      currentSlots = [];
      message.textContent = 'Availability could not be loaded. You can still check a time below.';
      message.dataset.connection = 'offline';
    }
  }
  picker.addEventListener('change', load);
  previous.addEventListener('click', () => {
    const nextDate = shiftDate(picker.value, -1);
    if (nextDate >= picker.min) {picker.value = nextDate; load();}
  });
  next.addEventListener('click', () => {
    const nextDate = shiftDate(picker.value, 1);
    if (nextDate <= picker.max) {picker.value = nextDate; load();}
  });
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') load();
  });
  window.setInterval(() => {
    if (document.visibilityState !== 'hidden') load();
  }, 30000);
  load();
})();
