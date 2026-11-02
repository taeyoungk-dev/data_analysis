"""Browser tests for the dashboard against a contract-compatible mock API (see mock_api.py)."""

import json
import re

from playwright.sync_api import Page, Route, expect


def open_dashboard(page: Page, base_url: str) -> None:
    page.goto(base_url + "/")
    expect(page.locator("#healthRanking .rank-button")).to_have_count(31)
    expect(page.locator("#specialtyList .specialty-row").first).to_be_visible()


def test_core_flow_renders_summary_rankings_detail_and_housing(page: Page, base_url: str) -> None:
    open_dashboard(page, base_url)

    expect(page.locator("#apiStatus")).to_have_text("API 연결됨")
    expect(page.locator("#healthCount")).to_have_text("31")
    expect(page.locator("#highPriorityCount")).to_have_text("7")
    expect(page.locator("#clinicCount")).to_have_text("12,140")
    expect(page.locator("#healthPeriod")).to_have_text("2025.04")
    expect(page.locator("#heroSignalTitle")).to_have_text("연천군")
    expect(page.locator("#heroBand")).to_have_text("높음")
    expect(page.locator("#detailRegion")).to_have_text("연천군")
    expect(page.locator("#specialtyList .specialty-row")).to_have_count(7)
    expect(page.locator("#housingLeader")).to_have_text("서초구")
    expect(page.locator("#housingTable tr")).to_have_count(25)
    expect(page.locator("#housingChart .housing-row")).to_have_count(8)
    expect(page.locator("#healthMap .map-point")).to_have_count(31)
    assert page.errors == []  # type: ignore[attr-defined]


def test_search_filter_sort_and_empty_result(page: Page, base_url: str) -> None:
    open_dashboard(page, base_url)

    page.fill("#regionSearch", "가평")
    expect(page.locator("#resultCount")).to_have_text("1개 지역")
    expect(page.locator("#healthTable tr")).to_have_count(1)
    expect(page.locator("#healthMap .map-point:not(.filtered)")).to_have_count(1)

    page.fill("#regionSearch", "없는지역")
    expect(page.locator("#resultCount")).to_have_text("0개 지역")
    expect(page.locator("#healthRanking")).to_contain_text("조건에 맞는 지역이 없습니다")
    expect(page.locator("#healthTable")).to_contain_text("조건에 맞는 지역이 없습니다")

    page.fill("#regionSearch", "")
    page.select_option("#bandFilter", "HIGH")
    expect(page.locator("#resultCount")).to_have_text("7개 지역")
    page.select_option("#bandFilter", "ALL")
    page.select_option("#healthSort", "region")
    expect(page.locator("#healthRanking .rank-region > span").first).to_have_text("가평군")


def test_selecting_a_region_updates_detail_and_specialties(page: Page, base_url: str) -> None:
    open_dashboard(page, base_url)

    page.locator("#healthRanking .rank-button", has_text="가평군").click()

    expect(page.locator("#detailRegion")).to_have_text("가평군")
    expect(page.locator("#specialtyList .specialty-row").first).to_contain_text("내과")
    selected = page.locator("#healthRanking .rank-button[aria-pressed='true']")
    expect(selected).to_have_count(1)
    expect(selected).to_contain_text("가평군")


def test_keyboard_users_can_select_from_table_and_map(page: Page, base_url: str) -> None:
    open_dashboard(page, base_url)

    page.click("summary")
    row = page.locator("#healthTable tr", has_text="양평군")
    row.focus()
    page.keyboard.press("Enter")
    expect(page.locator("#detailRegion")).to_have_text("양평군")

    point = page.locator("#healthMap .map-point[aria-label^='여주시']")
    point.focus()
    tooltip = page.locator("#mapTooltip")
    expect(tooltip).to_be_visible()
    expect(tooltip).to_contain_text("여주시")
    left = tooltip.evaluate("element => element.style.left")
    assert re.fullmatch(r"\d+(\.\d+)?px", left), left  # positioned even without a pointer
    page.keyboard.press(" ")
    expect(page.locator("#detailRegion")).to_have_text("여주시")


def test_api_failure_shows_error_state_and_retry_recovers(page: Page, base_url: str) -> None:
    calls = {"overview": 0}

    def fail(route: Route) -> None:
        calls["overview"] += 1
        route.fulfill(status=503, body="{}", content_type="application/json")

    page.route("**/api/v1/overview", fail)
    page.goto(base_url + "/")

    expect(page.locator("#errorToast")).to_be_visible()
    expect(page.locator("#apiStatus")).to_have_text("API 연결 실패")
    expect(page.locator("#healthRanking")).to_contain_text("데이터를 불러오지 못했습니다")
    expect(page.locator("#housingTable")).to_contain_text("데이터를 불러오지 못했습니다")

    page.unroute("**/api/v1/overview")
    page.locator("#retryButton").click()
    expect(page.locator("#errorToast")).to_be_hidden()
    expect(page.locator("#healthRanking .rank-button")).to_have_count(31)
    assert calls["overview"] == 1


def test_retry_ignores_duplicate_clicks_while_loading(page: Page, base_url: str) -> None:
    page.route("**/api/v1/overview", lambda route: route.fulfill(status=500, body="{}"))
    page.goto(base_url + "/")
    expect(page.locator("#errorToast")).to_be_visible()
    page.unroute("**/api/v1/overview")

    requests: list[str] = []
    page.on("request", lambda request: requests.append(request.url))
    page.locator("#retryButton").evaluate("button => { button.click(); button.click(); button.click(); }")
    expect(page.locator("#healthRanking .rank-button")).to_have_count(31)
    assert sum(url.endswith("/api/v1/overview") for url in requests) == 1


def test_specialty_failure_is_contained_to_its_panel(page: Page, base_url: str) -> None:
    page.route("**/specialties", lambda route: route.fulfill(status=500, body="{}"))
    page.goto(base_url + "/")

    expect(page.locator("#healthRanking .rank-button")).to_have_count(31)
    expect(page.locator("#specialtyList")).to_contain_text("진료과목 데이터를 불러오지 못했습니다")
    expect(page.locator("#errorToast")).to_be_hidden()


def test_empty_api_data_shows_empty_states_without_script_errors(page: Page, base_url: str) -> None:
    empty_overview = {
        "healthRegions": 0,
        "highPriorityRegions": 0,
        "activeClinics": 0,
        "housingRegions": 0,
        "highestHealthPriority": None,
        "hottestHousingMarket": None,
        "generatedFrom": "test",
    }
    page.route(
        "**/api/v1/overview",
        lambda route: route.fulfill(json=empty_overview),
    )
    page.route(re.compile(r".*/api/v1/(health-access|housing)\?.*"), lambda r: r.fulfill(json=[]))
    page.goto(base_url + "/")

    expect(page.locator("#apiStatus")).to_have_text("API 연결됨")
    expect(page.locator("#healthRanking")).to_contain_text("표시할 지역 데이터가 없습니다")
    expect(page.locator("#housingTable")).to_contain_text("데이터가 없습니다")
    expect(page.locator("#specialtyList")).to_contain_text("표시할 진료과목 데이터가 없습니다")
    assert page.errors == []  # type: ignore[attr-defined]


def test_stalled_request_times_out_into_error_state(page: Page, base_url: str) -> None:
    page.clock.install()
    page.route("**/api/v1/overview", lambda route: None)  # never answers
    page.goto(base_url + "/")
    page.clock.run_for(11_000)

    expect(page.locator("#errorToast")).to_be_visible()
    expect(page.locator("#healthRanking")).to_contain_text("데이터를 불러오지 못했습니다")


def test_mobile_layout_has_no_horizontal_scroll(browser, base_url: str) -> None:
    context = browser.new_context(viewport={"width": 375, "height": 812}, is_mobile=True)
    page = context.new_page()
    try:
        open_dashboard(page, base_url)
        overflow = page.evaluate(
            "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"
        )
        assert overflow <= 0, f"page overflows horizontally by {overflow}px"
        expect(page.locator("#regionSearch")).to_be_visible()
    finally:
        context.close()


def test_mock_contract_matches_api_validation(page: Page, base_url: str) -> None:
    response = page.request.get(base_url + "/api/v1/health-access?limit=99")
    assert response.status == 400
    assert json.loads(response.text())["status"] == 400
