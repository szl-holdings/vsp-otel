# SPDX-License-Identifier: Apache-2.0
# © 2026 SZL Holdings — Yachay (CTO) + Perplexity Computer Agent
# Doctrine v11 LOCKED — 749/14/163 · Λ = Conjecture 1
"""Real exporter test: a mock OTLP receiver captures exported span batches."""

from __future__ import annotations

from vsp_otel.exporter import Welford, VSPExporterConfig, build_exporter


class _MockOTLPReceiver:
    """Stand-in for the upstream OTLPSpanExporter — captures batches.

    Implements the SpanExporter protocol so VSPSpanExporter can delegate to it
    exactly as it would to the real gRPC exporter.
    """

    def __init__(self):
        self.batches = []
        self.shutdown_called = False

    def export(self, spans):
        self.batches.append(list(spans))
        return "SUCCESS"

    def shutdown(self):
        self.shutdown_called = True

    def force_flush(self, timeout_millis=30000):
        return True


def test_exporter_delegates_and_records_fanout():
    recv = _MockOTLPReceiver()
    exp = build_exporter(VSPExporterConfig(endpoint="http://mock:4317"),
                         inner=recv)

    exp.export(["s1", "s2", "s3"])
    exp.export(["s4"])

    # Spans actually reached the (mock) OTLP receiver, in the right batches.
    assert len(recv.batches) == 2
    assert recv.batches[0] == ["s1", "s2", "s3"]
    assert recv.batches[1] == ["s4"]

    # Fan-out (Welford) recorded batch sizes 3 and 1.
    snap = exp.fanout_snapshot()
    assert snap["n"] == 2
    assert abs(snap["mean"] - 2.0) < 1e-9


def test_exporter_shutdown_and_flush_delegate():
    recv = _MockOTLPReceiver()
    exp = build_exporter(inner=recv)
    assert exp.force_flush() is True
    exp.shutdown()
    assert recv.shutdown_called is True


def test_build_exporter_raises_without_otlp_package(monkeypatch):
    """HONESTY: with no inner and no OTLP package, we raise — not silent no-op."""
    import builtins
    real_import = builtins.__import__

    def fake_import(name, *a, **k):
        if name.startswith("opentelemetry.exporter.otlp"):
            raise ImportError("simulated missing otlp")
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    try:
        build_exporter(VSPExporterConfig())
        assert False, "expected RuntimeError"
    except RuntimeError as e:
        assert "otlp" in str(e).lower()


def test_welford_matches_numpy_style_variance():
    w = Welford()
    data = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
    for x in data:
        w.update(x)
    # Population mean=5, population variance=4, stddev=2 (classic example).
    assert abs(w.mean - 5.0) < 1e-9
    assert abs(w.variance - 4.0) < 1e-9
    assert abs(w.stddev - 2.0) < 1e-9


def test_config_from_env(monkeypatch):
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://collector:4317")
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_HEADERS", "x-api-key=abc,team=mesh")
    cfg = VSPExporterConfig.from_env()
    assert cfg.endpoint == "http://collector:4317"
    assert cfg.headers["x-api-key"] == "abc"
    assert cfg.headers["team"] == "mesh"


# ---------------------------------------------------------------------------
# Fail-closed config validation (adversarial).
#
# HONESTY: a configured endpoint STRING is not proof a collector exists — but an
# empty / malformed / self-inconsistent endpoint is proof one does NOT. These
# tests pin the fail-closed behaviour so a service can never *claim* span export
# it is not actually wired to perform.
# ---------------------------------------------------------------------------
import math  # noqa: E402

import pytest  # noqa: E402


def test_validate_accepts_ordinary_endpoints():
    # Scheme-ful http (plaintext + insecure) and scheme-less host:port are both
    # legitimate OTLP/gRPC targets and must pass unchanged.
    assert VSPExporterConfig(endpoint="http://collector:4317",
                             insecure=True).validate().endpoint \
        == "http://collector:4317"
    # Scheme-less host[:port] — a valid gRPC form that urlparse mis-reads as a
    # scheme; validation must NOT reject it (regression guard).
    VSPExporterConfig(endpoint="collector:4317", insecure=True).validate()
    VSPExporterConfig(endpoint="tempo.observability.svc:4317").validate()
    # TLS endpoint with insecure=False is consistent and allowed.
    VSPExporterConfig(endpoint="https://collector:4317", insecure=False).validate()


def test_validate_rejects_empty_endpoint():
    with pytest.raises(ValueError) as ei:
        VSPExporterConfig(endpoint="").validate()
    assert "empty" in str(ei.value).lower()
    # whitespace-only is also empty
    with pytest.raises(ValueError):
        VSPExporterConfig(endpoint="   ").validate()


def test_validate_rejects_non_http_scheme():
    with pytest.raises(ValueError) as ei:
        VSPExporterConfig(endpoint="ftp://collector:4317").validate()
    assert "scheme" in str(ei.value).lower()


def test_validate_rejects_scheme_without_host():
    with pytest.raises(ValueError) as ei:
        VSPExporterConfig(endpoint="http://", insecure=True).validate()
    assert "host" in str(ei.value).lower()
    with pytest.raises(ValueError):
        VSPExporterConfig(endpoint="http://:4317", insecure=True).validate()


def test_validate_rejects_tls_scheme_insecure_mismatch():
    # https target but plaintext requested — would silently drop every span.
    with pytest.raises(ValueError) as ei:
        VSPExporterConfig(endpoint="https://collector:4317",
                          insecure=True).validate()
    assert "inconsistent" in str(ei.value).lower()
    # http target but TLS demanded — the mirror inconsistency.
    with pytest.raises(ValueError):
        VSPExporterConfig(endpoint="http://collector:4317",
                          insecure=False).validate()


def test_validate_rejects_bad_timeout():
    for bad in (0.0, -1.0, float("nan"), float("inf")):
        with pytest.raises(ValueError):
            VSPExporterConfig(endpoint="http://c:4317", insecure=True,
                              timeout_s=bad).validate()
    # a finite positive timeout is fine
    assert math.isfinite(
        VSPExporterConfig(endpoint="http://c:4317", insecure=True,
                          timeout_s=5.0).validate().timeout_s)


def test_build_exporter_fails_closed_on_empty_endpoint():
    """Factory refuses to build an exporter aimed at nothing (fail-closed).

    Validation runs before any inner exporter is constructed, so an unusable
    endpoint is rejected regardless of transport availability.
    """
    with pytest.raises(ValueError):
        build_exporter(VSPExporterConfig(endpoint=""))


def test_install_degrades_honestly_on_invalid_config():
    """middleware.install must NOT raise on a bad endpoint; it degrades to
    no-export and says so honestly (never claims export it cannot do)."""
    pytest.importorskip("opentelemetry.sdk.trace")
    import vsp_otel.middleware as mw

    cfg = mw.VSPConfig(otlp=VSPExporterConfig(endpoint=""))
    status = mw.install(app=None, config=cfg)

    assert status.otlp_exporter is False
    note = status.note.lower()
    assert "invalid" in note or "inconsistent" in note
