import json

from c311.logging_utils import configure_logging
from c311.metrics import LogMetrics, Metrics


def _last_record(capfd):
    return json.loads(capfd.readouterr().out.strip().splitlines()[-1])


def test_incr_emits_counter_line(capfd):
    configure_logging()
    LogMetrics().incr("c311.extract.rows", 1000, source="soda")
    rec = _last_record(capfd)
    assert rec["event"] == "metric"
    assert rec["metric"] == "c311.extract.rows"
    assert rec["kind"] == "counter"
    assert rec["value"] == 1000
    assert rec["tags"] == {"source": "soda"}


def test_incr_defaults_to_one(capfd):
    configure_logging()
    LogMetrics().incr("c311.extract.pages")
    assert _last_record(capfd)["value"] == 1


def test_gauge_emits_gauge_line(capfd):
    configure_logging()
    LogMetrics().gauge("c311.freshness.lag_seconds", 42.5)
    rec = _last_record(capfd)
    assert rec["kind"] == "gauge" and rec["value"] == 42.5


def test_tag_named_value_does_not_collide(capfd):
    configure_logging()
    LogMetrics().incr("c311.quality.check_failed", value=2, severity="error")
    assert _last_record(capfd)["tags"] == {"severity": "error"}


class FakeMetrics:
    """What call-site tests will pass in: records calls, no logging."""

    def __init__(self):
        self.calls = []

    def incr(self, name, value=1, **tags):
        self.calls.append(("incr", name, value, tags))

    def gauge(self, name, value, **tags):
        self.calls.append(("gauge", name, value, tags))


def test_fake_satisfies_protocol():
    m: Metrics = FakeMetrics()  # mypy checks this structurally
    m.incr("c311.extract.rows", 5)
    assert m.calls == [("incr", "c311.extract.rows", 5, {})]
