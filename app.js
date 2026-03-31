let trains = [];
let stations = new Set();

async function load() {
  const res = await fetch('./trains.json');
  const data = await res.json();

  trains = data.map(convert);

  trains.forEach(t => {
    t.stops.forEach(s => stations.add(s.station));
  });

  setup();
}

function convert(t) {
  let stops = [];

  for (let i = 0; i < t.stanice.length; i++) {
    let name = t.stanice[i]
      .replace(" (Arr)", "")
      .replace(" (Dep)", "");

    stops.push({
      station: name,
      time: t.vreme[i]
    });
  }

  return {
    line: t.linija || "",
    stops
  };
}

function setup() {
  const select = document.getElementById("stationSelect");

  [...stations].sort().forEach(s => {
    select.innerHTML += `<option>${s}</option>`;
  });

  select.onchange = render;
  render();
}

function render() {
  const station = document.getElementById("stationSelect").value;
  const output = document.getElementById("output");

  output.innerHTML = "";

  trains.forEach(t => {
    const stop = t.stops.find(s => s.station === station);

    if (stop) {
      output.innerHTML += `
        <div class="card pids">
          ${t.line} → ${stop.time}
        </div>
      `;
    }
  });
}

load();
