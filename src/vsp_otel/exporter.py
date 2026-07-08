# SPDX-License-Identifier: Apache-2.0
# © 2026 SZL Holdings — Yachay (CTO) + Perplexity Computer Agent
# Doctrine v11 LOCKED — 749/14/163 · Λ = Conjecture 1
"""Real OTLP/gRPC span exporter for the SZL mesh.

This wraps the upstream ``opentelemetry-exporter-otlp-proto-grpc`` exporter so
spans actually leave the process over the wire to an OpenTelemetry Collector.
The collector then fans the spans out to Jaeger + Tempo + the SZL custom Khipu
exporter (see ``deploy/otel-collector-config.yaml``).

Design notes
------------
* This is a thin, honest wrapper. We do NOT reimplement gRPC/OTLP — we delegate
  to the upstream ``OTLPSpanExporter`` which is the maintained reference client.
* The wrapper adds:
    - env-driven configuration (``OTEL_EXPORTER_OTLP_ENDPOINT``, headers, TLS)
    - a Welford online estimator of trace fan-out (spans-per-export-batch) so the
      mesh can report variance of batch sizes without storing every sample
    - a clean ``build_exporter()`` factory used by the middleware

If the upstream OTLP package is not importable, ``build_exporter`` raises a clear
``RuntimeError`` rather than silently no-op'ing — the caller (middleware) decides
whether to degrade gracefully.
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass, field
from typing import Mapping, Sequence
from urllib.parse import urlparse


# ---------------------------------------------------------------------------
# Welford online variance — used for trace fan-out (batch-size) statistics.
# Numerically stable single-pass mean/variance. Pure stdlib; always available.
# ---------------------------------------------------------------------------
class Welford:
    """Online mean/variance (Welford's algorithm).

    Used here for the online variance of *trace fan-out* — i.e. how many spans
    are flushed per export batch. Lets the mesh emit a stable variance estimate
    without retaining samples. (See ARCH.md "Formula tie-ins".)
    """

    __slots__ = ("n", "mean", "_m2")

    def __init__(self) -> None:
        self.n = 0
        self.mean = 0.0
        self._m2 = 0.0

    def update(self, x: float) -> None:
        self.n += 1
        delta = x - self.mean
        self.mean += delta / self.n
        delta2 = x - self.mean
        self._m2 += delta * delta2

    @property
    def variance(self) -> float:
        # population variance (sample variance is _m2/(n-1)); 0 for n<2
        return self._m2 / self.n if self.n >= 1 else 0.0

    @property
    def sample_variance(self) -> float:
        return self._m2 / (self.n - 1) if self.n >= 2 else 0.0

    @property
    def stddev(self) -> float:
        return math.sqrt(self.variance)

    def snapshot(self) -> dict:
        return {
            "n": self.n,
            "mean": self.mean,
            "variance": self.variance,
            "sample_variance": self.sample_variance,
            "stddev": self.stddev,
        }


@dataclass
class VSPExporterConfig:
    """Configuration for the OTLP/gRPC exporter.

    Resolution order: explicit kwargs > environment > defaults.
    """

    endpoint: str = field(default_factory=lambda: os.environ.get(
        "OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"))
    insecure: bool = field(default_factory=lambda: os.environ.get(
        "OTEL_EXPORTER_OTLP_INSECURE", "true").lower() in ("1", "true", "yes"))
    headers: Mapping[str, str] = field(default_factory=dict)
    timeout_s: float = field(default_factory=lambda: float(
        os.environ.get("OTEL_EXPORTER_OTLP_TIMEOUT", "10")))

    @classmethod
    def from_env(cls) -> "VSPExporterConfig":
        hdrs = {}
        raw = os.environ.get("OTEL_EXPORTER_OTLP_HEADERS", "")
        for pair in raw.split(","):
            if "=" in pair:
                k, v = pair.split("=", 1)
                hdrs[k.strip()] = v.strip()
        return cls(headers=hdrs)

    def validate(self) -> "VSPExporterConfig":
        """Fail-closed validation of the exporter's collector target.

        HONESTY: a configured endpoint STRING is *not* proof that a real
        collector exists — but an endpoint that is empty, malformed, or
        self-inconsistent is proof that one does **not**. We reject those up
        front (fail-closed) rather than handing a hollow target to the OTLP
        exporter, which would silently drop every span and let a service *claim*
        span provenance it never actually exported.

        Checks (first failure wins, with a specific, actionable message):

        * endpoint is non-empty (an empty endpoint is not a collector);
        * if a URL scheme is present it is ``http`` / ``https`` and carries a
          host (``ftp://…`` / ``http://`` alone can never reach a collector);
        * scheme⇄``insecure`` are consistent — an ``https://`` target with
          ``insecure=True`` would send plaintext to a TLS port (and an
          ``http://`` target with ``insecure=False`` would attempt TLS against a
          plaintext port), silently dropping every span;
        * ``timeout_s`` is a finite, strictly-positive number of seconds.

        Scheme-less ``host[:port]`` endpoints (a valid OTLP/gRPC form, e.g.
        ``collector:4317``) are accepted; only the presence of a host is
        required in that case.

        Returns ``self`` on success so calls can be chained; raises
        ``ValueError`` on the first inconsistency.
        """
        ep = (self.endpoint or "").strip()
        if not ep:
            raise ValueError(
                "OTLP endpoint is empty — refusing to build an exporter with no "
                "collector target (an empty endpoint is not a collector)."
            )

        if "://" in ep:
            parsed = urlparse(ep)
            scheme = parsed.scheme.lower()
            if scheme not in ("http", "https"):
                raise ValueError(
                    f"OTLP endpoint scheme {scheme!r} is not routable to a "
                    f"collector — expected 'http' or 'https' (got {ep!r})."
                )
            if not parsed.hostname:
                raise ValueError(
                    f"OTLP endpoint {ep!r} has a scheme but no host — "
                    "not a collector target."
                )
            if scheme == "https" and self.insecure:
                raise ValueError(
                    "Inconsistent OTLP config: endpoint is 'https://' (TLS) but "
                    "insecure=True (plaintext). Set insecure=False or use "
                    "'http://'."
                )
            if scheme == "http" and not self.insecure:
                raise ValueError(
                    "Inconsistent OTLP config: endpoint is 'http://' (plaintext) "
                    "but insecure=False (TLS demanded). Set insecure=True or use "
                    "'https://'."
                )
        else:
            # Scheme-less host[:port]; strip an optional :port and /path.
            host = ep.split("/", 1)[0].rsplit(":", 1)[0]
            if not host:
                raise ValueError(
                    f"OTLP endpoint {ep!r} has no host — not a collector target."
                )

        if not math.isfinite(self.timeout_s) or self.timeout_s <= 0:
            raise ValueError(
                "OTLP timeout must be a finite, positive number of seconds, got "
                f"{self.timeout_s!r}."
            )

        return self


class VSPSpanExporter:
    """Decorator over the upstream OTLP gRPC exporter.

    Implements the OpenTelemetry ``SpanExporter`` protocol (``export``,
    ``shutdown``, ``force_flush``) by delegating to the wrapped exporter and
    folding each batch's span count into the Welford fan-out estimator.
    """

    def __init__(self, inner, fanout: Welford | None = None) -> None:
        self._inner = inner
        self.fanout = fanout if fanout is not None else Welford()

    def export(self, spans: Sequence):
        # Record fan-out (batch size) before delegating.
        self.fanout.update(float(len(spans)))
        return self._inner.export(spans)

    def shutdown(self) -> None:
        return self._inner.shutdown()

    def force_flush(self, timeout_millis: int = 30_000) -> bool:
        # Upstream gRPC exporter exposes force_flush in recent versions.
        ff = getattr(self._inner, "force_flush", None)
        return ff(timeout_millis) if callable(ff) else True

    # Convenience for diagnostics / the /provenance board.
    def fanout_snapshot(self) -> dict:
        return self.fanout.snapshot()


def build_exporter(config: VSPExporterConfig | None = None,
                   inner=None) -> VSPSpanExporter:
    """Build a real OTLP/gRPC span exporter.

    Parameters
    ----------
    config : VSPExporterConfig, optional
        Endpoint / TLS / header / timeout configuration. Defaults to env.
    inner : SpanExporter, optional
        Inject a pre-built inner exporter (used by tests with a mock receiver).
        When omitted, the upstream ``OTLPSpanExporter`` is constructed.

    Returns
    -------
    VSPSpanExporter
        A ``SpanExporter``-compatible object ready to attach to a
        ``BatchSpanProcessor``.

    Raises
    ------
    ValueError
        If the resolved configuration does not describe a usable collector
        target (empty / malformed / self-inconsistent endpoint, or a non-finite
        / non-positive timeout). Fail-closed: we never build an exporter aimed at
        nothing, which would drop spans silently (HONESTY OVER CHECKLIST).
    RuntimeError
        If ``inner`` is not supplied and the upstream OTLP gRPC package is not
        installed. We raise rather than silently no-op (HONESTY OVER CHECKLIST).
    """
    cfg = (config or VSPExporterConfig.from_env()).validate()
    if inner is None:
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                OTLPSpanExporter,
            )
        except ImportError as e:  # pragma: no cover - exercised in degraded envs
            raise RuntimeError(
                "opentelemetry-exporter-otlp-proto-grpc is not installed; "
                "cannot build a real OTLP exporter. Install vsp-otel[otlp]."
            ) from e
        inner = OTLPSpanExporter(
            endpoint=cfg.endpoint,
            insecure=cfg.insecure,
            headers=dict(cfg.headers) or None,
            timeout=int(cfg.timeout_s),
        )
    return VSPSpanExporter(inner)
