let trains = [];
let stations = new Set();

/* Load JSON */
async function loadData() {
  const res = await fetch('./data/trains.json');
  const data = await res.json();

  trains = data.map(train => ({
    ...train,
    stops: normalizeStops(train.stops)
  }));

  trains.forEach(t => {
    t.stops.forEach(s => stations.add(s.station));
  });

  populateSelectors();
}

/* Normalize ARR/DEP */
function normalizeStops(stops) {
  const map = {};

  stops.forEach(s => {
    let name = s.station
      .replace(" (Arr)", "")
      .replace(" (Dep)", "");

    if (!map[name]) {
      map[name] = { station: name };
    }

    if (s.station.includes("(Arr)")) {
      map[name].arrival = s.time;
    } else if (s.station.includes("(Dep)")) {
      map[name].departure = s.time;
    } else {
      map[name].arrival = s.time;
      map[name].departure = s.time;
    }
  });

  return Object.values(map);
}

/* UI Navigation */
function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}

/* Populate dropdowns */
function populateSelectors() {
  const stationSelect = document.getElementById("stationSelect");
  const from = document.getElementById("from");
  const to = document.getElementById("to");

  stations.forEach(s => {
    stationSelect.innerHTML += `<option>${s}</option>`;
    from.innerHTML += `<option>${s}</option>`;
    to.innerHTML += `<option>${s}</option>`;
  });

  stationSelect.onchange = renderPIDS;
}

/* PIDS */
function renderPIDS() {
  const station = document.getElementById("stationSelect").value;
  const container = document.getElementById("departures");

  container.innerHTML = "";

  trains.forEach(train => {
    const stop = train.stops.find(s => s.station === station);

    if (stop && stop.departure) {
      container.innerHTML += `
        <div class="glass pids-text">
          ${train.line || ''} → ${train.destination || ''}
          <br/>
          ${stop.departure}
        </div>
      `;
    }
  });
}

/* Planner */
function planRoute() {
  const from = document.getElementById("from").value;
  const to = document.getElementById("to").value;
  const container = document.getElementById("results");

  container.innerHTML = "";

  trains.forEach(train => {
    const fromStop = train.stops.find(s => s.station === from);
    const toStop = train.stops.find(s => s.station === to);

    if (fromStop && toStop) {
      container.innerHTML += `
        <div class="glass">
          ${train.line || ''} <br/>
          ${from} (${fromStop.departure}) → ${to} (${toStop.arrival})
        </div>
      `;
    }
  });
}

/* Init */
loadData();

/* Register Service Worker */
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('service-worker.js');
}
