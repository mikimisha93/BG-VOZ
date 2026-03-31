let trains = [];
let stations = new Set();

/* LOAD DATA */
async function loadData() {
  const res = await fetch('./trains.json'); // simpler path
  const data = await res.json();

  trains = data.map(t => convertTrain(t));

  trains.forEach(t => {
    t.stops.forEach(s => stations.add(s.station));
  });

  populateSelectors();

  // auto render first station
  renderPIDS();
}

/* 🔥 CONVERT YOUR JSON FORMAT */
function convertTrain(train) {
  const stops = [];

  for (let i = 0; i < train.stanice.length; i++) {
    const rawName = train.stanice[i];
    const time = train.vreme[i];

    let name = rawName
      .replace(" (Arr)", "")
      .replace(" (Dep)", "");

    let existing = stops.find(s => s.station === name);

    if (!existing) {
      existing = { station: name };
      stops.push(existing);
    }

    if (rawName.includes("(Arr)")) {
      existing.arrival = time;
    } else if (rawName.includes("(Dep)")) {
      existing.departure = time;
    } else {
      existing.arrival = time;
      existing.departure = time;
    }
  }

  return {
    line: train.linija || "",
    destination: stops[stops.length - 1]?.station,
    stops
  };
}

/* NAVIGATION */
function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}

/* DROPDOWNS */
function populateSelectors() {
  const stationSelect = document.getElementById("stationSelect");
  const from = document.getElementById("from");
  const to = document.getElementById("to");

  const sorted = Array.from(stations).sort();

  sorted.forEach(s => {
    stationSelect.innerHTML += `<option value="${s}">${s}</option>`;
    from.innerHTML += `<option value="${s}">${s}</option>`;
    to.innerHTML += `<option value="${s}">${s}</option>`;
  });
}

/* 🚉 PIDS */
function renderPIDS() {
  const station = document.getElementById("stationSelect").value;
  const container = document.getElementById("departures");

  container.innerHTML = "";

  trains.forEach(train => {
    const stop = train.stops.find(s => s.station === station);

    if (stop && stop.departure) {
      container.innerHTML += `
        <div class="glass pids-text">
          ${train.line} → ${train.destination}<br/>
          ${stop.departure}
        </div>
      `;
    }
  });
}

/* 🧭 PLANNER */
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
          ${train.line}<br/>
          ${from} (${fromStop.departure || "-"}) → 
          ${to} (${toStop.arrival || "-"})
        </div>
      `;
    }
  });
}

/* INIT */
loadData();

/* SW */
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('./service-worker.js');
}
