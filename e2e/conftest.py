from collections.abc import Iterator

import pytest
from playwright.sync_api import Browser, Page, sync_playwright

from mock_api import start_server


@pytest.fixture(scope="session")
def base_url() -> Iterator[str]:
    server, url = start_server()
    yield url
    server.shutdown()


@pytest.fixture(scope="session")
def browser() -> Iterator[Browser]:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        yield browser
        browser.close()


@pytest.fixture
def page(browser: Browser) -> Iterator[Page]:
    context = browser.new_context(viewport={"width": 1280, "height": 900}, locale="ko-KR")
    page = context.new_page()
    page.errors = []  # type: ignore[attr-defined]
    page.on("pageerror", lambda error: page.errors.append(str(error)))  # type: ignore[attr-defined]
    yield page
    context.close()
