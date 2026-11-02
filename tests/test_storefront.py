import re

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, expect

from conftest import check_domain, random_domain

pytestmark = pytest.mark.ui

STOREFRONT_URL = "https://www.wix.com/domains"
TAKEN_DOMAIN = "mybakery.com"


def search(page, query):
    """Type the query in the storefront search box, press Enter and return
    the check-domain-availability response.
    The tests never click "Get It" or "Make It Yours"."""
    page.goto(STOREFRONT_URL, wait_until="load")
    box = page.locator("input:visible").first
    expect(box).to_be_visible()
    expect(box).to_be_enabled()
    box.fill(query)
    # If Enter is pressed before the page's scripts are ready, the search is
    # silently ignored (seen in a debug run). So if no search call goes out,
    # press Enter one more time. Each try waits up to 10 seconds.
    for attempt in range(2):
        try:
            with page.expect_response(lambda r: "check-domain-availability" in r.url, timeout=10000) as check_info:
                box.press("Enter")
            return check_info.value
        except PlaywrightTimeoutError:
            pass
    pytest.fail(f"Pressed Enter twice for '{query}', but no check-domain-availability call was sent")


@pytest.fixture(scope="module")
def taken_search(browser):
    # One search shared by SF-01, SF-03, SF-04 and E-01, to keep page loads low.
    page = browser.new_page()
    # 60 seconds: covers the page load plus both Enter tries inside search().
    with page.expect_response(lambda r: "suggest-domains" in r.url, timeout=60000) as suggest_info:
        check_response = search(page, TAKEN_DOMAIN)
    # The card title <h1> counts as hidden (its text is in a hidden span), so wait for the card.
    page.locator("[data-hook='main-card-0']").wait_for()
    yield {
        "page": page,
        "check": check_response.json(),
        "suggest": suggest_info.value.json(),
    }
    page.close()


def test_sf_01_taken_domain_shows_registered_and_alternatives(taken_search):
    page = taken_search["page"]
    assert page.get_by_text("is already registered").is_visible()
    assert page.locator("[data-hook='main-card-0']").is_visible()


def test_sf_02_random_domain_shows_available(page):
    domain = random_domain()
    search(page, domain)
    hero = page.locator("[data-hook='hero-card']")
    hero.wait_for()
    assert "Available now!" in hero.inner_text()
    # Long names are shortened on screen, e.g. "qa-4ca67c...74ed1815c.com".
    # Check that the start and the end shown belong to the searched domain.
    shown = page.locator("[data-hook='hero-card-title']").text_content()
    start, _, end = shown.partition("...")
    assert domain.startswith(start)
    assert domain.endswith(end)


def test_sf_03_registered_message_names_the_domain(taken_search):
    # Guards against F1 (FINDINGS.md) coming back: the message was missing the domain name.
    message = taken_search["page"].get_by_text("is already registered").inner_text()
    assert TAKEN_DOMAIN in message


def test_sf_04_suggestions_on_screen_come_from_suggest_domains(taken_search):
    page = taken_search["page"]
    response_names = [s["domain"] for s in taken_search["suggest"]["suggestions"]]

    # The two main cards and the list items below them.
    items = page.locator("[data-hook='main-card-0-title'], [data-hook='main-card-1-title']").all()
    for el in page.locator("[data-hook^='recommendations-content-list-item-']").all():
        if re.fullmatch(r"recommendations-content-list-item-\d+", el.get_attribute("data-hook")):
            items.append(el)

    shown_names = []
    for el in items:
        text = el.text_content()
        # The longest response name inside this item's text is the name it shows.
        matches = [name for name in response_names if name in text]
        assert matches, f"An item on screen is not in the response: {text[:80]}"
        shown_names.append(max(matches, key=len))

    assert len(shown_names) > 0
    assert len(shown_names) == len(set(shown_names)), "A domain is shown twice"


def test_e01_storefront_and_public_api_agree(taken_search):
    storefront_answer = taken_search["check"]["availability"]["available"]
    api_response = check_domain(TAKEN_DOMAIN)
    assert api_response.status_code == 200
    assert api_response.json()["availability"]["available"] == storefront_answer
