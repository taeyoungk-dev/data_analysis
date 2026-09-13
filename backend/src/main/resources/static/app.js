const integer = new Intl.NumberFormat("ko-KR");
const compactWon = (value) => {
  const eok = Number(value) / 100_000_000;
  return `${eok.toLocaleString("ko-KR", { maximumFractionDigits: 1 })}억`;
};

const createBars = (element, items, valueKey) => {
  element.replaceChildren(...items.slice(0, 7).map((item) => {
    const row = document.createElement("div");
    row.className = "bar-row";
    row.innerHTML = `
      <strong>${item.region}</strong>
      <div class="bar-track"><div class="bar-fill" style="width:${item[valueKey]}%"></div></div>
      <span class="bar-value">${Number(item[valueKey]).toFixed(0)}</span>`;
    return row;
  }));
};

const healthRow = (item) => `
  <tr>
    <td>${item.region}</td>
    <td>${integer.format(item.elderlyPopulation)}</td>
    <td>${integer.format(item.activeClinics)}</td>
    <td>${Number(item.clinicsPer10kElderly).toFixed(2)}</td>
    <td>${Number(item.priorityScore).toFixed(1)}</td>
  </tr>`;

const housingRow = (item) => `
  <tr>
    <td>${item.region}</td>
    <td>${integer.format(item.transactionCount)}</td>
    <td>${compactWon(item.medianTradePriceKrw)}</td>
    <td>${Number(item.priceCagrPct).toFixed(2)}%</td>
    <td>${Number(item.marketHeatScore).toFixed(1)}</td>
  </tr>`;

async function loadDashboard() {
  try {
    const [overviewResponse, healthResponse, housingResponse] = await Promise.all([
      fetch("/api/v1/overview"),
      fetch("/api/v1/health-access?limit=10"),
      fetch("/api/v1/housing?limit=10"),
    ]);
    if (![overviewResponse, healthResponse, housingResponse].every((response) => response.ok)) {
      throw new Error("API response was not successful");
    }
    const [overview, health, housing] = await Promise.all([
      overviewResponse.json(), healthResponse.json(), housingResponse.json(),
    ]);

    document.querySelector("#healthCount").textContent = overview.healthRegions;
    document.querySelector("#housingCount").textContent = overview.housingRegions;
    document.querySelector("#healthTable").innerHTML = health.map(healthRow).join("");
    document.querySelector("#housingTable").innerHTML = housing.map(housingRow).join("");
    createBars(document.querySelector("#healthChart"), health, "priorityScore");
    createBars(document.querySelector("#housingChart"), housing, "marketHeatScore");
  } catch (error) {
    const message = '<p class="error">API 연결에 실패했습니다. 서버와 데이터베이스 상태를 확인해 주세요.</p>';
    document.querySelector("#healthChart").innerHTML = message;
    document.querySelector("#housingChart").innerHTML = message;
    console.error(error);
  }
}

loadDashboard();

