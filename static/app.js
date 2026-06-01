const map = L.map("map", { preferCanvas: true }).setView([23.75, 121.0], 7);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
}).addTo(map);

const layer = L.layerGroup().addTo(map);
const summary = document.querySelector("#summary");
const list = document.querySelector("#temple-list");
const query = document.querySelector("#query");
const city = document.querySelector("#city");
const deity = document.querySelector("#deity");
const search = document.querySelector("#search");

let markers = new Map();
let metaCache = null;

function label(value, fallback = "尚未提供") {
  return value === null || value === undefined || value === "" ? fallback : value;
}

function yesNo(value) {
  if (value === true) return "有";
  if (value === false) return "無";
  return "待補";
}

function popupHtml(temple) {
  return `
    <div class="popup">
      <h2>${label(temple.name)}</h2>
      <p><strong>地址</strong>：${label(temple.address)}</p>
      <p><strong>主祀</strong>：${label(temple.main_deity)}</p>
      <p><strong>營業時間</strong>：${label(temple.opening_hours)}</p>
      <p><strong>供水</strong>：${yesNo(temple.has_water)}　<strong>供餐</strong>：${yesNo(temple.has_meals)}</p>
      <p><strong>電話</strong>：${label(temple.phone)}</p>
    </div>
  `;
}

function templeItem(temple) {
  const button = document.createElement("button");
  button.className = "temple";
  button.innerHTML = `
    <strong>${label(temple.name)}</strong>
    <span>${label(temple.address)}</span>
    <small>主祀：${label(temple.main_deity)}｜營業時間：${label(temple.opening_hours)}</small>
    <span class="tags">
      <span class="tag">${label(temple.city)}</span>
      <span class="tag">供水：${yesNo(temple.has_water)}</span>
      <span class="tag">供餐：${yesNo(temple.has_meals)}</span>
    </span>
  `;
  button.addEventListener("click", () => {
    const marker = markers.get(temple.id);
    if (!marker) return;
    map.setView(marker.getLatLng(), 16);
    marker.openPopup();
  });
  return button;
}

async function loadMeta() {
  const meta = await fetch("/api/meta").then((response) => response.json());
  metaCache = meta;
  summary.textContent = `官方資料 ${meta.count.toLocaleString()} 筆，可上圖 ${meta.mapped.toLocaleString()} 筆`;

  for (const item of meta.cities) {
    const option = new Option(item, item);
    city.append(option);
  }
  for (const item of meta.deities) {
    const option = new Option(item, item);
    deity.append(option);
  }
}

async function loadTemples() {
  const wantsAllTaiwan = !query.value.trim() && !city.value && !deity.value;
  const params = new URLSearchParams({
    q: query.value,
    city: city.value,
    deity: deity.value,
    limit: wantsAllTaiwan && metaCache ? String(metaCache.mapped) : "3000",
  });
  const temples = await fetch(`/api/temples?${params}`).then((response) => response.json());
  const scope = wantsAllTaiwan ? "全台灣" : "目前條件";
  const total = wantsAllTaiwan && metaCache ? metaCache.mapped : temples.length;
  summary.textContent = `${scope}顯示 ${temples.length.toLocaleString()} 筆，資料庫可上圖 ${total.toLocaleString()} 筆`;

  layer.clearLayers();
  markers = new Map();
  list.innerHTML = "";

  const bounds = [];
  for (const temple of temples) {
    const point = [temple.latitude, temple.longitude];
    bounds.push(point);
    const marker = L.circleMarker(point, {
      radius: 6,
      weight: 1,
      color: "#8f2d24",
      fillColor: "#b43b2e",
      fillOpacity: 0.82,
    }).bindPopup(popupHtml(temple));
    marker.addTo(layer);
    markers.set(temple.id, marker);
    list.append(templeItem(temple));
  }

  if (bounds.length) {
    map.fitBounds(bounds, { padding: [36, 36], maxZoom: 12 });
  }
  if (!temples.length) {
    list.innerHTML = '<p class="empty">找不到符合條件的公廟。</p>';
  }
}

search.addEventListener("click", loadTemples);
query.addEventListener("keydown", (event) => {
  if (event.key === "Enter") loadTemples();
});
city.addEventListener("change", loadTemples);
deity.addEventListener("change", loadTemples);

loadMeta().then(loadTemples);
