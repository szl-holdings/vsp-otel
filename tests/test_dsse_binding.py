# SPDX-License-Identifier: Apache-2.0
# © 2026 SZL Holdings — Yachay (CTO) + Perplexity Computer Agent
# Doctrine v11 LOCKED — 749/14/163 · Λ = Conjecture 1
"""DSSE binding tests: envelope is well-formed DSSEv1, PAE is spec-correct,
and the Khipu chain hash-links correctly."""

from __future__ import annotations

import base64
import hashlib
import hmac

from vsp_otel import ATTR_RECEIPT_HASH, ATTR_KHIPU_INDEX
from vsp_otel.dsse_processor import (
    DSSEKhipuSpanProcessor,
    KhipuChain,
    PAYLOAD_TYPE,
    dsse_envelope,
    dsse_pae,
)


# --- Lightweight span stub (duck-typed like an OTel ReadableSpan) ---------
class _Ctx:
    def __init__(self, trace_id, span_id):
        self.trace_id = trace_id
        self.span_id = span_id


class SpanStub:
    def __init__(self, name, trace_id, span_id, attributes=None):
        self.name = name
        self.context = _Ctx(trace_id, span_id)
        self.attributes = dict(attributes or {})

    def set_attribute(self, k, v):
        self.attributes[k] = v


def test_pae_matches_dsse_spec_examples():
    # From the DSSE spec test vectors: type="http://example.com/HelloWorld",
    # body="hello world". PAE = "DSSEv1 29 <type> 11 hello world".
    pae = dsse_pae("http://example.com/HelloWorld", b"hello world")
    assert pae == b"DSSEv1 29 http://example.com/HelloWorld 11 hello world"


def test_envelope_is_well_formed_dssev1():
    payload = b'{"hello":"world"}'
    key = b"k"
    env = dsse_envelope(payload, PAYLOAD_TYPE,
                        lambda d: hmac.new(key, d, hashlib.sha256).digest(),
                        keyid="kid-1")
    # Required DSSE v1 fields.
    assert set(env.keys()) == {"payload", "payloadType", "signatures"}
    assert env["payloadType"] == PAYLOAD_TYPE
    # payload is base64 of the raw payload.
    assert base64.standard_b64decode(env["payload"]) == payload
    # exactly one signature with keyid + base64 sig.
    assert len(env["signatures"]) == 1
    sig = env["signatures"][0]
    assert sig["keyid"] == "kid-1"
    raw_sig = base64.standard_b64decode(sig["sig"])
    # Signature is over the PAE — verify it.
    expected = hmac.new(key, dsse_pae(PAYLOAD_TYPE, payload),
                        hashlib.sha256).digest()
    assert raw_sig == expected


def test_signature_is_over_pae_not_raw_payload():
    payload = b"abc"
    key = b"k"
    env = dsse_envelope(payload, PAYLOAD_TYPE,
                        lambda d: hmac.new(key, d, hashlib.sha256).digest())
    raw_sig = base64.standard_b64decode(env["signatures"][0]["sig"])
    over_raw = hmac.new(key, payload, hashlib.sha256).digest()
    over_pae = hmac.new(key, dsse_pae(PAYLOAD_TYPE, payload),
                        hashlib.sha256).digest()
    assert raw_sig != over_raw          # NOT signed over the raw payload
    assert raw_sig == over_pae          # signed over the PAE (anti-confusion)


def test_processor_binds_span_and_stamps_receipt_hash():
    chain = KhipuChain()
    proc = DSSEKhipuSpanProcessor(chain=chain)
    span = SpanStub("GET /x", trace_id=0x1234, span_id=0xabcd,
                    attributes={"http.method": "GET"})
    proc.on_start(span)
    proc.on_end(span)

    assert len(chain) == 1
    # The span now carries the receipt hash + khipu index.
    assert ATTR_RECEIPT_HASH in span.attributes
    assert span.attributes[ATTR_KHIPU_INDEX] == 0
    r = chain.receipts()[0]
    assert r.receipt_hash == span.attributes[ATTR_RECEIPT_HASH]
    # Envelope on the chain is well-formed.
    assert r.envelope["payloadType"] == PAYLOAD_TYPE


def test_khipu_chain_hash_links_and_verifies():
    chain = KhipuChain()
    proc = DSSEKhipuSpanProcessor(chain=chain)
    for i in range(5):
        proc.on_end(SpanStub(f"op{i}", trace_id=i + 1, span_id=i + 100,
                             attributes={"i": i}))
    receipts = chain.receipts()
    assert len(receipts) == 5
    # Genesis link.
    assert receipts[0].prev == "0" * 64
    # Each receipt's prev == previous receipt's link.
    for a, b in zip(receipts, receipts[1:]):
        assert b.prev == a.link
    assert chain.verify() is True


def test_rekor_index_stamped_when_submit_supplied():
    chain = KhipuChain()
    proc = DSSEKhipuSpanProcessor(chain=chain,
                                  rekor_submit=lambda env: 424242)
    proc.on_end(SpanStub("op", 1, 2, {"a": 1}))
    r = chain.receipts()[0]
    assert r.rekor_log_index == 424242


def test_rekor_index_absent_when_no_submit():
    chain = KhipuChain()
    proc = DSSEKhipuSpanProcessor(chain=chain)  # no rekor_submit
    proc.on_end(SpanStub("op", 1, 2, {"a": 1}))
    assert chain.receipts()[0].rekor_log_index is None  # never fabricated


# --- Real OpenTelemetry SDK spans (immutable ReadableSpan in on_end) ------
def _sdk_pipeline(chain, **proc_kwargs):
    import pytest
    pytest.importorskip("opentelemetry.sdk.trace")
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
        InMemorySpanExporter,
    )

    provider = TracerProvider()
    proc = DSSEKhipuSpanProcessor(chain=chain, **proc_kwargs)
    provider.add_span_processor(proc)  # must precede the export processor
    exported = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exported))
    return provider, proc, exported


def test_sdk_exported_span_carries_its_chained_receipt():
    """Regression: the receipt used to stay in process memory only.

    Real SDKs pass on_end an immutable ReadableSpan, so set_attribute-based
    stamping never reached the exporter (opentelemetry-sdk 1.25-1.45).
    """
    from vsp_otel import ATTR_DSSE_PAYLOAD_TYPE, ATTR_KHIPU_PREV, ATTR_REKOR_LOG_INDEX

    chain = KhipuChain()
    provider, proc, exported = _sdk_pipeline(chain, rekor_submit=lambda env: 7)
    tracer = provider.get_tracer("vsp-otel-test")
    for i in range(3):
        with tracer.start_as_current_span(f"op{i}") as span:
            span.set_attribute("app.i", i)
    provider.shutdown()

    spans = exported.get_finished_spans()
    receipts = chain.receipts()
    assert len(spans) == len(receipts) == 3
    for span, receipt in zip(spans, receipts):
        assert span.attributes[ATTR_RECEIPT_HASH] == receipt.receipt_hash
        assert span.attributes[ATTR_KHIPU_INDEX] == receipt.index
        assert span.attributes[ATTR_KHIPU_PREV] == receipt.prev
        assert span.attributes[ATTR_DSSE_PAYLOAD_TYPE] == PAYLOAD_TYPE
        assert span.attributes[ATTR_REKOR_LOG_INDEX] == 7
        assert span.attributes["app.i"] == receipt.index  # app data untouched
    assert proc.stamp_failures == 0 and proc.bind_failures == 0
    assert chain.verify() is True


def test_unstampable_span_is_counted_not_silently_passed():
    class Opaque:  # neither set_attribute nor an attribute map to replace
        name = "opaque"
        context = _Ctx(1, 2)
        attributes = {"a": 1}

    chain = KhipuChain()
    proc = DSSEKhipuSpanProcessor(chain=chain)
    proc.on_end(Opaque())
    assert len(chain) == 1          # the receipt is still chained in process
    assert proc.stamp_failures == 1  # ...but the gap is visible


def test_signer_failure_does_not_raise_into_the_app_and_is_counted():
    def broken_signer(_data):
        raise RuntimeError("signing backend unavailable")

    chain = KhipuChain()
    proc = DSSEKhipuSpanProcessor(chain=chain, signer=broken_signer, keyid="k")
    span = SpanStub("op", 1, 2, {"a": 1})
    proc.on_end(span)  # must not raise into the instrumented application
    assert proc.bind_failures == 1
    assert len(chain) == 0
    assert ATTR_RECEIPT_HASH not in span.attributes


def test_repeated_failures_are_counted_but_logged_loudly_once(caplog):
    import logging

    def broken_signer(_data):
        raise RuntimeError("signing backend unavailable")

    proc = DSSEKhipuSpanProcessor(chain=KhipuChain(), signer=broken_signer)
    with caplog.at_level(logging.DEBUG, logger="vsp_otel.dsse_processor"):
        for i in range(3):
            proc.on_end(SpanStub(f"op{i}", 1, i + 1, {"a": i}))
    assert proc.bind_failures == 3
    loud = [r for r in caplog.records if r.levelno >= logging.WARNING]
    assert len(loud) == 1 and "bind_failures=1" in loud[0].getMessage()
