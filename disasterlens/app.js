let commandMap, reportMiniMap, reportMiniMarker, landingMap;

const API_BASE = "http://127.0.0.1:8000";

const WS_BASE = "ws://127.0.0.1:8000/ws";



// Store markers to avoid duplicates

const mapMarkers = {};

let currentFilter = 'all';

let activeCount = 0;



function getHazardColor(hazardType) {

  if (!hazardType) return '#9ca3af';

  const t = hazardType.toLowerCase();

  if (t.includes('flood') || t.includes('water')) return '#3b82f6'; // Blue

  if (t.includes('fire')) return '#ef4444'; // Red

  if (t.includes('struct') || t.includes('damage')) return '#eab308'; // Yellow

  return '#9ca3af';

}



function plotReportOnMap(map, report) {

  if (!map) return;

  const color = getHazardColor(report.hazard_type);



  const innerRadius = L.circle([report.lat, report.lon], {
    radius: 400, // Inner danger zone (High risk)
    color: '#ef4444',
    fillColor: '#ef4444',
    fillOpacity: 0.35,
    weight: 1,
    interactive: false
  });

  const outerRadius = L.circle([report.lat, report.lon], {
    radius: 1200, // Outer danger zone (Moderate risk)
    color: '#eab308',
    fillColor: '#eab308',
    fillOpacity: 0.15,
    weight: 1,
    dashArray: '4',
    interactive: false
  });

  const centerPoint = L.circleMarker([report.lat, report.lon], {
    radius: 8,
    fillColor: color,
    color: '#ffffff',
    weight: 2,
    opacity: 1,
    fillOpacity: 0.9
  })
    .bindPopup(`<strong>Report #${report.id}</strong><br>${report.hazard_type} (${report.severity.toUpperCase()})<br><span style="font-family: monospace; font-size: 0.9em; color: #888;">${report.lat.toFixed(5)}, ${report.lon.toFixed(5)}</span>`)
    .bindTooltip(`${report.lat.toFixed(5)}, ${report.lon.toFixed(5)}`, { direction: 'top', opacity: 0.8 });

  const marker = L.layerGroup([outerRadius, innerRadius, centerPoint]);

  marker.hazard_type = report.hazard_type;

  marker.severity = report.severity.toLowerCase();



  // Initially add to map only if it matches current filter

  let show = false;

  if (currentFilter === 'all') show = true;

  else if (currentFilter === 'High' && marker.severity === 'high') show = true;

  else if (marker.hazard_type.includes(currentFilter)) show = true;



  if (show) marker.addTo(map);



  if (!mapMarkers[report.id]) mapMarkers[report.id] = [];

  mapMarkers[report.id].push({ map, marker });

}



function updateLiveFeed(report) {

  const feed = document.getElementById("incident-feed-list");

  if (!feed) return;

  const color = getHazardColor(report.hazard_type);

  

  const div = document.createElement("div");

  div.className = "feed-item";

  div.style.cursor = "pointer";

  div.dataset.hazard = report.hazard_type;

  div.dataset.severity = report.severity.toLowerCase();

  

  div.onclick = () => {

    const targetZoom = 16;

    if (commandMap) commandMap.flyTo([report.lat, report.lon], targetZoom, { animate: true, duration: 1.5 });

    if (landingMap) landingMap.flyTo([report.lat, report.lon], targetZoom, { animate: true, duration: 1.5 });

    

    setTimeout(() => {

      if (mapMarkers[report.id]) {

        mapMarkers[report.id].forEach(obj => obj.marker.openPopup());

      }

    }, 1500);

  };



  let timeStr = "JUST NOW";

  if (report.created_at) {

    let dateStr = report.created_at;

    if (dateStr.indexOf(' ') !== -1 && !dateStr.endsWith('Z')) {

      dateStr = dateStr.replace(' ', 'T') + 'Z';

    }

    const dateObj = new Date(dateStr);

    if (!isNaN(dateObj)) {

      timeStr = new Intl.DateTimeFormat('en-GB', { 

        timeZone: 'Asia/Kolkata', hour12: false, 

        hour: '2-digit', minute:'2-digit', second:'2-digit' 

      }).format(dateObj) + ' IST';

    }

  }



  div.innerHTML = `

    <div class="feed-item-top">

      <span class="feed-badge" style="background: ${color}33; color: ${color};">${report.hazard_type}</span>

      <span class="feed-time">${timeStr}</span>

    </div>

    <div class="feed-location">Lat: ${report.lat.toFixed(4)}, Lon: ${report.lon.toFixed(4)}</div>

    <div class="feed-meta">

      <span>Conf: ${(report.hazard_confidence * 100).toFixed(1)}%</span>

      <span>Severity: ${report.severity.toUpperCase()}</span>

    </div>

  `;

  feed.prepend(div);

  

  applyFilter(currentFilter); // Re-run filter to update display and counts

}



function applyFilter(filter) {

  currentFilter = filter;

  

  // Update buttons

  document.querySelectorAll(".map-filter-btn").forEach(btn => {

     if (btn.dataset.filter === filter) btn.classList.add("active");

     else btn.classList.remove("active");

  });



  activeCount = 0;



  // Filter feed items

  document.querySelectorAll(".feed-item").forEach(el => {

    const hazard = el.dataset.hazard;

    const severity = el.dataset.severity;

    

    let show = false;

    if (filter === 'all') show = true;

    else if (filter === 'High' && severity === 'high') show = true;

    else if (hazard.includes(filter)) show = true;

    

    if (show) {

      el.style.display = "block";

      activeCount++;

    } else {

      el.style.display = "none";

    }

  });



  // Update feed count

  const indicator = document.getElementById("feed-count-indicator");

  if (indicator) indicator.innerText = `${activeCount} ACTIVE`;

  

  const navIndicator = document.getElementById("nav-count-indicator");

  if (navIndicator) navIndicator.innerText = `${activeCount} ACTIVE`;



  // Filter map markers

  Object.values(mapMarkers).forEach(markerObjects => {

    markerObjects.forEach(({map, marker}) => {

       const hazard = marker.hazard_type;

       const severity = marker.severity;

       

       let show = false;

       if (filter === 'all') show = true;

       else if (filter === 'High' && severity === 'high') show = true;

       else if (hazard.includes(filter)) show = true;

       

       if (show) {

          if (!map.hasLayer(marker)) marker.addTo(map);

       } else {

          if (map.hasLayer(marker)) marker.remove();

       }

    });

  });

}





async function loadReports() {

  try {

    const res = await fetch(`${API_BASE}/reports`);

    if (!res.ok) throw new Error("Failed to fetch");

    const reports = await res.json();

    

    // Plot on maps

    reports.forEach(r => {

      if (commandMap) plotReportOnMap(commandMap, r);

      if (landingMap) plotReportOnMap(landingMap, r);

      updateLiveFeed(r);

    });

  } catch (err) {

    console.error("Error loading reports:", err);

  }

}



function connectWebSocket() {

  const ws = new WebSocket(WS_BASE);

  ws.onmessage = (event) => {

    const data = JSON.parse(event.data);

    if (data.type === "new_report" && data.report) {

      if (commandMap) plotReportOnMap(commandMap, data.report);

      if (landingMap) plotReportOnMap(landingMap, data.report);

      updateLiveFeed(data.report);

    }

  };

  ws.onclose = () => setTimeout(connectWebSocket, 5000);

}



// ----------------------------------------------------

// MAP INITIALIZATION

// ----------------------------------------------------



function initCommandCenterMap() {

  const mapContainer = document.getElementById("command-center-map");

  if (!mapContainer) return;



  commandMap = L.map("command-center-map", {

    center: [37.7780, -122.4150],

    zoom: 13,

    zoomControl: false,

    attributionControl: false

  });



  L.control.zoom({ position: "topright" }).addTo(commandMap);

  const osmDark = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", { className: "dark-layer", maxZoom: 19 }).addTo(commandMap);

  const esriSatellite = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", { maxZoom: 19 });



  L.control.layers({ "Tactical Dark (OSM)": osmDark, "Live Satellite (Esri)": esriSatellite }, null, { position: "topleft" }).addTo(commandMap);

}



function initLeafletLandingMap() {

  const mapContainer = document.getElementById("response-leaflet-map");

  if (!mapContainer) return;



  landingMap = L.map("response-leaflet-map", {

    center: [37.7749, -122.4194],

    zoom: 13,

    zoomControl: true,

    attributionControl: false

  });



  const osmDark = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", { className: "dark-layer", maxZoom: 19 }).addTo(landingMap);

  const esriSatellite = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", { maxZoom: 19 });



  L.control.layers({ "Tactical Dark (OSM)": osmDark, "Live Satellite (Esri)": esriSatellite }, null, { position: "topleft" }).addTo(landingMap);

}



function initOrUpdateReportMiniMap(lat, lng) {

  const mapContainer = document.getElementById("report-mini-map");

  if (!mapContainer) return;



  if (!reportMiniMap) {

    reportMiniMap = L.map("report-mini-map", {

      center: [lat, lng],

      zoom: 14,

      zoomControl: false,

      attributionControl: false,

      dragging: true

    });



    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", { className: "dark-layer", maxZoom: 19 }).addTo(reportMiniMap);



    reportMiniMarker = L.circleMarker([lat, lng], {

      radius: 8,

      fillColor: '#3b82f6',

      color: '#ffffff',

      weight: 2,

      opacity: 1,

      fillOpacity: 0.9

    })

      .bindPopup(`<strong>Incident Location</strong><br><span style="font-family: monospace; color: #888;">${lat.toFixed(5)}, ${lng.toFixed(5)}</span>`)

      .bindTooltip(`${lat.toFixed(5)}, ${lng.toFixed(5)}`, { direction: 'top', permanent: true, opacity: 0.8, offset: [0, -10] })

      .addTo(reportMiniMap);

  } else {

    reportMiniMap.setView([lat, lng], 14);

    if (reportMiniMarker) {

      reportMiniMarker.setLatLng([lat, lng])

        .setPopupContent(`<strong>Incident Location</strong><br><span style="font-family: monospace; color: #888;">${lat.toFixed(5)}, ${lng.toFixed(5)}</span>`)

        .setTooltipContent(`${lat.toFixed(5)}, ${lng.toFixed(5)}`);

    }

  }



  setTimeout(() => reportMiniMap.invalidateSize(), 200);

}



// ----------------------------------------------------

// UI FUNCTIONS

// ----------------------------------------------------



let currentLat = 37.7749;

let currentLon = -122.4194;



function openReportModal() { document.getElementById("report-damage-modal")?.classList.add("active"); }

function closeReportModal() { document.getElementById("report-damage-modal")?.classList.remove("active"); }

function openJudgeModal() { document.getElementById("judge-drawer")?.classList.add("open"); }

function closeJudgeModal() { document.getElementById("judge-drawer")?.classList.remove("open"); }

function switchHudCase(idx) { console.log("HUD Case switched to", idx); }

function runSimDemo(type) { console.log("Running simulation demo for:", type); }



function refreshDeviceLocation() {

  const text = document.getElementById("modal-gps-text");

  if (text) text.innerText = "Acquiring GPS lock...";

  

  if (navigator.geolocation) {

    navigator.geolocation.getCurrentPosition(

      (pos) => {

        currentLat = pos.coords.latitude;

        currentLon = pos.coords.longitude;

        if (text) text.innerText = `LOCKED: ${currentLat.toFixed(4)}°, ${currentLon.toFixed(4)}°`;

        if (document.getElementById("report-mini-map")) {

           initOrUpdateReportMiniMap(currentLat, currentLon);

        }

      },

      (err) => {

        console.warn("GPS error, using mock coords", err);

        currentLat = 37.7749 + (Math.random() * 0.02 - 0.01);

        currentLon = -122.4194 + (Math.random() * 0.02 - 0.01);

        if (text) text.innerText = `MOCK LOCKED: ${currentLat.toFixed(4)}°, ${currentLon.toFixed(4)}°`;

      }

    );

  } else {

    if (text) text.innerText = `GPS NOT SUPPORTED`;

  }

}



async function submitDamageReport(event) {

  event.preventDefault();

  const btn = document.getElementById("modal-submit-btn");

  if (btn) btn.innerHTML = '<span>Processing AI...</span>';

  

  const fileInput = document.getElementById("modal-file-input");

  const file = fileInput?.files[0];

  

  if (!file) {

    alert("Please select an image file first.");

    if (btn) btn.innerHTML = '<span>Classify & Broadcast Report</span>';

    return;

  }

  

  const formData = new FormData();

  formData.append("file", file);

  formData.append("lat", currentLat);

  formData.append("lon", currentLon);

  

  try {

    const res = await fetch(`${API_BASE}/submit`, {

      method: "POST",

      body: formData

    });

    

    if (!res.ok) {

      const errText = await res.text();

      throw new Error(`API failed (${res.status}): ${errText}`);

    }

    

    const report = await res.json();

    console.log("Report submitted successfully:", report);

    closeReportModal();

    alert(`Success! Classified as ${report.hazard_type} (${report.severity} severity).`);

  } catch (err) {

    console.error(err);

    alert("Error submitting report: " + err.message + "\n\nIs the backend server (run.bat) running?");

  } finally {

    if (btn) btn.innerHTML = '<i data-lucide="send" style="width: 14px; height: 14px;"></i><span>Classify & Broadcast Report</span>';

    if (typeof lucide !== 'undefined') lucide.createIcons();

  }

}



function handleModalFileSelect(event) {

  const text = document.getElementById("modal-upload-text");

  if (text && event.target.files.length > 0) {

    text.innerText = `Selected: ${event.target.files[0].name}`;

  }

}



document.addEventListener("DOMContentLoaded", () => {

  if (typeof lucide !== 'undefined') lucide.createIcons();

  

  document.querySelectorAll(".map-filter-btn").forEach(btn => {

    btn.addEventListener("click", (e) => {

      applyFilter(e.target.dataset.filter);

    });

  });

  

  if (document.getElementById("command-center-map")) initCommandCenterMap();

  if (document.getElementById("response-leaflet-map")) initLeafletLandingMap();

  if (document.getElementById("report-mini-map")) initOrUpdateReportMiniMap(currentLat, currentLon);

  

  // API Integration

  loadReports();

  connectWebSocket();

  

  const clockEl = document.getElementById('utc-clock');

  if (clockEl) {

    setInterval(() => {

      const now = new Date();

      const timeString = new Intl.DateTimeFormat('en-GB', {

        timeZone: 'Asia/Kolkata', hour12: false, 

        hour: '2-digit', minute:'2-digit', second:'2-digit'

      }).format(now);

      clockEl.textContent = timeString + ' IST';

    }, 1000);

  }

});

// --- STATS TICKER LOGIC ---
document.addEventListener("DOMContentLoaded", () => {
  const statReports = document.getElementById("stat-reports");
  const statHazards = document.getElementById("stat-hazards");
  
  if (statReports && statHazards) {
    let reportsCount = 120;
    let hazardsCount = 100;
    
    setInterval(() => {
        reportsCount += 1;
        statReports.textContent = reportsCount.toLocaleString();
        
        if (Math.random() < 0.833) {
            hazardsCount += 1;
            statHazards.textContent = hazardsCount.toLocaleString();
        }
    }, 360000);
  }
});
