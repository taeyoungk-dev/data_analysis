const integer = new Intl.NumberFormat("ko-KR");
const svgNamespace = "http://www.w3.org/2000/svg";
const REQUEST_TIMEOUT_MS = 10_000;
const HEALTH_LIMIT = 31;
const HOUSING_LIMIT = 25;
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

const state = {
  health: [],
  housing: [],
  selectedRegion: null,
  specialtyRequest: 0,
  loading: false,
};

const elements = {
  statusDot: document.querySelector("#statusDot"),
  apiStatus: document.querySelector("#apiStatus"),
  errorToast: document.querySelector("#errorToast"),
  retryButton: document.querySelector("#retryButton"),
  regionSearch: document.querySelector("#regionSearch"),
  bandFilter: document.querySelector("#bandFilter"),
  healthSort: document.querySelector("#healthSort"),
  resultCount: document.querySelector("#resultCount"),
  healthRanking: document.querySelector("#healthRanking"),
  healthMap: document.querySelector("#healthMap"),
  mapTooltip: document.querySelector("#mapTooltip"),
  healthTable: document.querySelector("#healthTable"),
  specialtyList: document.querySelector("#specialtyList"),
};

const setText = (selector, value) => {
  const element = document.querySelector(selector);
  if (element) element.textContent = value;
};

const formatWon = (value) => {
  const eok = Number(value) / 100_000_000;
  return `${eok.toLocaleString("ko-KR", { maximumFractionDigits: 1 })}억 원`;
};

const formatWonPerSqm = (value) => {
  const manwon = Number(value) / 10_000;
  return `${integer.format(Math.round(manwon))}만 원`;
};

const formatPeriod = (value) => {
  if (!value) return "—";
  const [year, month] = String(value).split("-");
  return month ? `${year}.${month}` : year;
};

const bandMeta = (band) => ({
  HIGH: { label: "높음", className: "high", color: "#d8613f" },
  WATCH: { label: "관찰", className: "watch", color: "#d59a2e" },
  BALANCED: { label: "균형", className: "balanced", color: "#4c8b78" },
}[band] || { label: band, className: "", color: "#63706b" });

async function fetchJson(url) {
  // A stalled connection must not leave the dashboard in a permanent loading state.
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    const response = await fetch(url, {
      headers: { Accept: "application/json" },
      signal: controller.signal,
    });
    if (!response.ok) throw new Error(`${url}: HTTP ${response.status}`);
    return await response.json();
  } finally {
    clearTimeout(timer);
  }
}

function message(text) {
  const element = document.createElement("p");
  element.className = "loading";
  element.textContent = text;
  return element;
}

function tableMessage(text, columns) {
  const row = document.createElement("tr");
  const cell = document.createElement("td");
  cell.colSpan = columns;
  cell.textContent = text;
  row.append(cell);
  return row;
}

function setApiStatus(online) {
  elements.statusDot.classList.toggle("online", online);
  elements.statusDot.classList.toggle("offline", !online);
  elements.apiStatus.textContent = online ? "API 연결됨" : "API 연결 실패";
}

function showError(error) {
  setApiStatus(false);
  elements.errorToast.hidden = false;
  const text = "데이터를 불러오지 못했습니다. 오른쪽 아래의 다시 시도를 눌러 주세요.";
  if (state.health.length === 0) {
    elements.resultCount.textContent = "—";
    elements.healthRanking.replaceChildren(message(text));
    elements.healthTable.replaceChildren(tableMessage(text, 7));
    elements.specialtyList.replaceChildren(message("진료과목 데이터를 불러오지 못했습니다."));
  }
  if (state.housing.length === 0) {
    setText("#housingLeaderMeta", text);
    document.querySelector("#housingTable").replaceChildren(tableMessage(text, 6));
  }
  console.error(error);
}

function hideError() {
  elements.errorToast.hidden = true;
}

function updateOverview(overview) {
  setText("#healthCount", integer.format(overview.healthRegions));
  setText("#highPriorityCount", integer.format(overview.highPriorityRegions));
  setText("#clinicCount", integer.format(overview.activeClinics));
  setText("#healthPeriod", formatPeriod(overview.highestHealthPriority?.period));

  const leader = overview.highestHealthPriority;
  if (leader) {
    const heroBand = document.querySelector("#heroBand");
    const meta = bandMeta(leader.priorityBand);
    heroBand.className = `band ${meta.className}`;
    heroBand.textContent = meta.label;
    setText("#heroSignalTitle", leader.region);
    setText("#heroPriorityScore", Number(leader.priorityScore).toFixed(1));
    setText("#heroElderlyShare", `${Number(leader.elderlySharePct).toFixed(1)}%`);
    setText("#heroClinicRate", Number(leader.clinicsPer10kElderly).toFixed(1));
  }
}

function filteredHealth() {
  const query = elements.regionSearch.value.trim().toLocaleLowerCase("ko-KR");
  const band = elements.bandFilter.value;
  const filtered = state.health.filter((item) => {
    const matchesQuery = item.region.toLocaleLowerCase("ko-KR").includes(query);
    const matchesBand = band === "ALL" || item.priorityBand === band;
    return matchesQuery && matchesBand;
  });

  const comparators = {
    priority: (a, b) => Number(b.priorityScore) - Number(a.priorityScore),
    elderly: (a, b) => Number(b.elderlySharePct) - Number(a.elderlySharePct),
    supply: (a, b) => Number(a.clinicsPer10kElderly) - Number(b.clinicsPer10kElderly),
    region: (a, b) => a.region.localeCompare(b.region, "ko-KR"),
  };
  return filtered.sort(comparators[elements.healthSort.value]);
}

function createBand(label) {
  const meta = bandMeta(label);
  const element = document.createElement("span");
  element.className = `band ${meta.className}`;
  element.textContent = meta.label;
  return element;
}

function renderRanking(items) {
  if (items.length === 0) {
    const text = state.health.length ? "조건에 맞는 지역이 없습니다. 검색어나 우선 구간을 바꿔 보세요." : "표시할 지역 데이터가 없습니다.";
    elements.healthRanking.replaceChildren(message(text));
    return;
  }

  const buttons = items.map((item, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "rank-button";
    button.classList.toggle("selected", item.region === state.selectedRegion);
    button.setAttribute("aria-pressed", String(item.region === state.selectedRegion));
    button.dataset.region = item.region;

    const rank = document.createElement("span");
    rank.className = "rank-number";
    rank.textContent = String(index + 1).padStart(2, "0");

    const region = document.createElement("span");
    region.className = "rank-region";
    const regionName = document.createElement("span");
    regionName.textContent = item.region;
    const meta = document.createElement("small");
    meta.textContent = `고령 ${Number(item.elderlySharePct).toFixed(1)}% · 1만 명당 ${Number(item.clinicsPer10kElderly).toFixed(1)}곳`;
    region.append(regionName, meta);

    const score = document.createElement("span");
    score.className = "rank-score";
    const scoreValue = document.createElement("strong");
    scoreValue.textContent = Number(item.priorityScore).toFixed(1);
    const scoreLabel = document.createElement("span");
    scoreLabel.textContent = bandMeta(item.priorityBand).label;
    score.append(scoreValue, scoreLabel);

    button.append(rank, region, score);
    button.addEventListener("click", () => selectRegion(item.region, true));
    return button;
  });
  elements.healthRanking.replaceChildren(...buttons);
}

function showMapTooltip(event, item) {
  const wrap = elements.healthMap.parentElement.getBoundingClientRect();
  // Keyboard focus has no pointer coordinates; anchor the tooltip to the focused point instead.
  let { clientX, clientY } = event;
  if (!Number.isFinite(clientX) || event.type === "focus") {
    const point = event.currentTarget.getBoundingClientRect();
    clientX = point.left + point.width / 2;
    clientY = point.top;
  }
  elements.mapTooltip.innerHTML = "";
  const title = document.createElement("strong");
  title.textContent = item.region;
  const score = document.createElement("span");
  score.textContent = `우선점수 ${Number(item.priorityScore).toFixed(1)}`;
  const supply = document.createElement("span");
  supply.textContent = `1만 명당 의원 ${Number(item.clinicsPer10kElderly).toFixed(1)}곳`;
  elements.mapTooltip.append(title, score, supply);
  elements.mapTooltip.hidden = false;
  elements.mapTooltip.style.left = `${Math.max(8, Math.min(clientX - wrap.left + 14, wrap.width - 170))}px`;
  elements.mapTooltip.style.top = `${Math.max(clientY - wrap.top - 30, 8)}px`;
}

function renderMap(visibleItems) {
  const valid = state.health.filter((item) => Number.isFinite(Number(item.latitude)) && Number.isFinite(Number(item.longitude)));
  if (valid.length === 0) return;
  const visibleRegions = new Set(visibleItems.map((item) => item.region));
  const latitudes = valid.map((item) => Number(item.latitude));
  const longitudes = valid.map((item) => Number(item.longitude));
  const minLat = Math.min(...latitudes);
  const maxLat = Math.max(...latitudes);
  const minLon = Math.min(...longitudes);
  const maxLon = Math.max(...longitudes);
  const x = (value) => 52 + ((Number(value) - minLon) / (maxLon - minLon || 1)) * 456;
  const y = (value) => 560 - ((Number(value) - minLat) / (maxLat - minLat || 1)) * 500;

  const background = document.createElementNS(svgNamespace, "rect");
  background.setAttribute("x", "24");
  background.setAttribute("y", "22");
  background.setAttribute("width", "512");
  background.setAttribute("height", "556");
  background.setAttribute("rx", "32");
  background.setAttribute("fill", "none");
  background.setAttribute("stroke", "rgba(18,55,47,.12)");
  background.setAttribute("stroke-dasharray", "4 7");

  const north = document.createElementNS(svgNamespace, "text");
  north.setAttribute("x", "38");
  north.setAttribute("y", "48");
  north.setAttribute("fill", "#63706b");
  north.setAttribute("font-size", "11");
  north.setAttribute("font-weight", "800");
  north.textContent = "N ↑";

  const groups = valid
    .sort((a, b) => Number(a.priorityScore) - Number(b.priorityScore))
    .map((item) => {
      const group = document.createElementNS(svgNamespace, "g");
      group.classList.add("map-point");
      if (!visibleRegions.has(item.region)) group.classList.add("filtered");
      if (item.region === state.selectedRegion) group.classList.add("selected");
      group.setAttribute("transform", `translate(${x(item.longitude)} ${y(item.latitude)})`);
      group.setAttribute("tabindex", "0");
      group.setAttribute("role", "button");
      group.setAttribute("aria-label", `${item.region}, 우선점수 ${Number(item.priorityScore).toFixed(1)}`);

      const circle = document.createElementNS(svgNamespace, "circle");
      circle.setAttribute("r", String(7 + Number(item.priorityScore) * .075));
      circle.setAttribute("fill", bandMeta(item.priorityBand).color);
      const label = document.createElementNS(svgNamespace, "text");
      label.setAttribute("y", String(22 + Number(item.priorityScore) * .075));
      label.textContent = item.region.replace(/[시군]$/, "");
      group.append(circle, label);

      group.addEventListener("pointerenter", (event) => showMapTooltip(event, item));
      group.addEventListener("pointermove", (event) => showMapTooltip(event, item));
      group.addEventListener("pointerleave", () => { elements.mapTooltip.hidden = true; });
      group.addEventListener("focus", (event) => showMapTooltip(event, item));
      group.addEventListener("blur", () => { elements.mapTooltip.hidden = true; });
      group.addEventListener("click", () => selectRegion(item.region, true));
      group.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          selectRegion(item.region, true);
        }
      });
      return group;
    });

  elements.healthMap.replaceChildren(background, north, ...groups);
}

function renderHealthTable(items) {
  if (items.length === 0) {
    const text = state.health.length ? "조건에 맞는 지역이 없습니다." : "표시할 지역 데이터가 없습니다.";
    elements.healthTable.replaceChildren(tableMessage(text, 7));
    return;
  }
  const rows = items.map((item) => {
    const row = document.createElement("tr");
    row.dataset.region = item.region;
    row.tabIndex = 0;
    row.setAttribute("aria-label", `${item.region} 상세 보기`);
    if (item.region === state.selectedRegion) row.setAttribute("aria-current", "true");
    const values = [
      item.region,
      `${Number(item.elderlySharePct).toFixed(1)}%`,
      integer.format(item.elderlyPopulation),
      integer.format(item.activeClinics),
      Number(item.clinicsPer10kElderly).toFixed(2),
      Number(item.priorityScore).toFixed(1),
    ];
    values.forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    });
    const bandCell = document.createElement("td");
    bandCell.append(createBand(item.priorityBand));
    row.append(bandCell);
    row.addEventListener("click", () => selectRegion(item.region, true));
    row.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        selectRegion(item.region, true);
      }
    });
    return row;
  });
  elements.healthTable.replaceChildren(...rows);
}

function renderHealthExplorer() {
  const items = filteredHealth();
  elements.resultCount.textContent = `${items.length}개 지역`;
  renderRanking(items);
  renderMap(items);
  renderHealthTable(items);
}

function detailSummary(item) {
  if (item.priorityBand === "HIGH") {
    return "고령인구 비율과 의원 공급을 함께 볼 때 세부 의료 접근성 점검이 우선되는 지역입니다.";
  }
  if (item.priorityBand === "WATCH") {
    return "상대적 수요와 공급을 지속 관찰하고 진료과목별 편차를 함께 확인할 지역입니다.";
  }
  return "경기도 내 상대 비교에서 수요와 의원 공급이 비교적 균형적인 지역입니다.";
}

function updateDetail(item) {
  const meta = bandMeta(item.priorityBand);
  setText("#detailRegion", item.region);
  const band = document.querySelector("#detailBand");
  band.className = `band ${meta.className}`;
  band.textContent = meta.label;
  setText("#detailSummary", detailSummary(item));
  setText("#detailScore", Number(item.priorityScore).toFixed(1));
  setText("#detailPopulation", `${integer.format(item.population)}명`);
  setText("#detailElderlyPopulation", `${integer.format(item.elderlyPopulation)}명`);
  setText("#detailElderlyShare", `${Number(item.elderlySharePct).toFixed(1)}%`);
  setText("#detailClinics", `${integer.format(item.activeClinics)}곳`);
  setText("#detailClinicRate", `${Number(item.clinicsPer10kElderly).toFixed(2)}곳`);
}

function renderSpecialties(items) {
  if (!items.length) {
    elements.specialtyList.replaceChildren(message("이 지역의 진료과목 데이터가 없습니다."));
    setText("#specialtySource", "—");
    return;
  }
  const maxDemand = Math.max(...items.map((item) => Number(item.diseaseSharePct)), 1);
  const maxSupply = Math.max(...items.map((item) => Number(item.clinicsPer10kElderly)), 1);
  const rows = items.map((item) => {
    const row = document.createElement("div");
    row.className = "specialty-row";
    const name = document.createElement("span");
    name.className = "specialty-name";
    name.textContent = item.specialty;

    const metric = (value, maximum, suffix, supply = false) => {
      const container = document.createElement("span");
      container.className = "mini-metric";
      const track = document.createElement("span");
      track.className = "mini-track";
      const fill = document.createElement("span");
      fill.className = `mini-fill${supply ? " supply" : ""}`;
      fill.style.width = `${Math.min(100, Math.max(2, Number(value) / maximum * 100))}%`;
      track.append(fill);
      const label = document.createElement("span");
      label.className = "mini-value";
      label.textContent = `${Number(value).toFixed(1)}${suffix}`;
      container.append(track, label);
      return container;
    };

    row.append(
      name,
      metric(item.diseaseSharePct, maxDemand, "%"),
      metric(item.clinicsPer10kElderly, maxSupply, "곳", true),
    );
    return row;
  });
  elements.specialtyList.replaceChildren(...rows);
  setText("#specialtySource", `${items[0].sourceScope} · ${items[0].sourcePeriod}`);
}

async function loadSpecialties(region) {
  const requestId = ++state.specialtyRequest;
  elements.specialtyList.replaceChildren(message("진료과목 데이터를 불러오는 중입니다."));
  try {
    const items = await fetchJson(`/api/v1/health-access/${encodeURIComponent(region)}/specialties`);
    if (requestId === state.specialtyRequest) renderSpecialties(items);
  } catch (error) {
    if (requestId !== state.specialtyRequest) return;
    elements.specialtyList.replaceChildren(
      message("진료과목 데이터를 불러오지 못했습니다. 지역을 다시 선택해 주세요."),
    );
    console.error(error);
  }
}

function selectRegion(region, scrollToDetail = false) {
  const item = state.health.find((candidate) => candidate.region === region);
  if (!item) return;
  state.selectedRegion = region;
  updateDetail(item);
  renderHealthExplorer();
  loadSpecialties(region);
  if (scrollToDetail) {
    document.querySelector("#regionDetail").scrollIntoView({
      behavior: reducedMotion.matches ? "auto" : "smooth",
      block: "start",
    });
  }
}

function renderHousing(items) {
  if (!items.length) {
    setText("#housingLeaderMeta", "표시할 주택시장 데이터가 없습니다.");
    document.querySelector("#housingTable").replaceChildren(tableMessage("데이터가 없습니다.", 6));
    return;
  }
  const leader = items[0];
  setText("#housingLeader", leader.region);
  setText("#housingLeaderScore", `${Number(leader.marketHeatScore).toFixed(1)}점`);
  setText(
    "#housingLeaderMeta",
    `중위 거래가 ${formatWon(leader.medianTradePriceKrw)} · 5년 CAGR ${Number(leader.priceCagrPct).toFixed(1)}%`,
  );

  const bars = items.slice(0, 8).map((item) => {
    const row = document.createElement("div");
    row.className = "housing-row";
    const region = document.createElement("strong");
    region.textContent = item.region;
    const track = document.createElement("span");
    track.className = "housing-track";
    const fill = document.createElement("span");
    fill.className = "housing-fill";
    fill.style.width = `${Math.min(100, Math.max(0, Number(item.marketHeatScore)))}%`;
    track.append(fill);
    const value = document.createElement("span");
    value.textContent = Number(item.marketHeatScore).toFixed(0);
    row.append(region, track, value);
    return row;
  });
  document.querySelector("#housingChart").replaceChildren(...bars);

  const rows = items.map((item) => {
    const row = document.createElement("tr");
    [
      item.region,
      integer.format(item.transactionCount),
      formatWon(item.medianTradePriceKrw),
      formatWonPerSqm(item.medianPricePerSqmKrw),
      `${Number(item.priceCagrPct).toFixed(2)}%`,
      Number(item.marketHeatScore).toFixed(1),
    ].forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    });
    return row;
  });
  document.querySelector("#housingTable").replaceChildren(...rows);
}

async function loadDashboard() {
  if (state.loading) return; // ignore repeated retry clicks while a request is in flight
  state.loading = true;
  elements.retryButton.disabled = true;
  hideError();
  elements.apiStatus.textContent = "연결 확인 중";
  elements.statusDot.classList.remove("online", "offline");
  try {
    const [overview, health, housing] = await Promise.all([
      fetchJson("/api/v1/overview"),
      fetchJson(`/api/v1/health-access?limit=${HEALTH_LIMIT}`),
      fetchJson(`/api/v1/housing?limit=${HOUSING_LIMIT}`),
    ]);
    state.health = health;
    state.housing = housing;
    updateOverview(overview);
    renderHousing(housing);
    setApiStatus(true);
    const selected = health.find((item) => item.region === state.selectedRegion) ?? health[0];
    if (selected) {
      selectRegion(selected.region);
    } else {
      renderHealthExplorer();
      elements.specialtyList.replaceChildren(message("표시할 진료과목 데이터가 없습니다."));
    }
  } catch (error) {
    showError(error);
  } finally {
    state.loading = false;
    elements.retryButton.disabled = false;
  }
}

[elements.regionSearch, elements.bandFilter, elements.healthSort].forEach((control) => {
  control.addEventListener(control === elements.regionSearch ? "input" : "change", renderHealthExplorer);
});
elements.retryButton.addEventListener("click", loadDashboard);

loadDashboard();
