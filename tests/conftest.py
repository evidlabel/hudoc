import pytest

from hudoc.fetcher import Response


class FakeHttp:
    """Stands in for ``http_get``: canned responses per URL, in order."""

    def __init__(self):
        self.routes = {}
        self.history = []

    @staticmethod
    def _response(status_code=200, text="", content=None, exc=None):
        if exc is not None:
            return Response(0, error=str(exc))
        return Response(status_code, content if content is not None else text.encode())

    def add(self, url, responses=None, **kwargs):
        """One response from kwargs, or a list of dicts served in turn (the last repeats)."""
        self.routes[url] = [self._response(**r) for r in responses or [kwargs]]

    def __call__(self, url, timeout=None):
        self.history.append(url)
        responses = self.routes.get(url)
        if not responses:
            return Response(0, error=f"no route for {url}")
        return responses.pop(0) if len(responses) > 1 else responses[0]


@pytest.fixture
def fake_http(monkeypatch):
    fake = FakeHttp()
    monkeypatch.setattr("hudoc.fetcher.http_get", fake)
    monkeypatch.setattr("hudoc.core.parser.http_get", fake)
    return fake
