let trains = [];
let stations = new Set();

async function load() {
  const res = await fetch('trains.json');
  const data = await res.json();

  // ✅ NO conversion needed anymore
  trains = data;

  // collect stations (clean names without Arr/Dep)
  trains.forEach(t => {
    t.stops.forEach(s => {
      const name = cleanStation(s.station);
      stations.add(name);
    });
  });

  setup();
}

/* 🧹 REMOVE (Arr) / (Dep) */
function cleanStation(name) {
  return name
    .replace(" (Arr)", "")
    .replace(" (Dep)", "");
}

/* SETUP DROPDOWN */
function setup() {
  const select = document.getElementById("stationSelect");

  const sorted = [...stations].sort();

  sorted.forEach(s => {
    select.innerHTML += `<option value="${s}">${s}</option>`;
  });

  // 👇 important so something shows
  select.value = sorted[0];

  select.onchange = render;

  render();
}

/* 🚆 RENDER TRAINS */
function render() {
  const station = document.getElementById("stationSelect").value;
  const output = document.getElementById("output");

  output.innerHTML = "";

  trains.forEach(t => {

    // find BOTH Arr/Dep versions
    const stop = t.stops.find(s =>
      cleanStation(s.station) === station &&
      s.station.includes("(Dep)") // 👈 only show departures
    );

    if (stop) {
      output.innerHTML += `
        <div class="card pids">
          ${t.line} → ${t.direction}<br>
          ${stop.departure}
        </div>
      `;
    }
  });
}

load();
