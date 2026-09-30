"""Real loopback delivery, signed provenance, and failure/retry boundaries."""
from __future__ import annotations

import base64
import copy
import hashlib
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi.testclient import TestClient

from collector import app as collector
from collector import lambda_gate
from collector.dsse import DsseSigner, _pae, _in_toto_statement


def payload():
    return {"resourceSpans": [{"resource": {"attributes": [{"key": "service.name", "value": {"stringValue": "fixture-router"}}]},
        "scopeSpans": [{"scope": {"name": "test-only"}, "spans": [{
            "traceId": "1" * 32, "spanId": "2" * 16, "name": "fixture.inference",
            "startTimeUnixNano": "1", "endTimeUnixNano": "1000001",
            "attributes": [{"key": f"lambda.a{i}", "value": {"doubleValue": 0.97}} for i in range(1, 6)]}]}]}]}


@pytest.fixture
def configured(monkeypatch):
    key = ec.generate_private_key(ec.SECP256R1())
    pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                            serialization.NoEncryption()).decode()
    monkeypatch.setenv("VSP_SIGN_KEY_PEM", pem)
    monkeypatch.setenv("VSP_SIGN_MODE", "ecdsa")
    monkeypatch.setattr(collector, "SIGNER", DsseSigner())
    monkeypatch.setattr(collector, "COUNTERS", dict.fromkeys(collector.COUNTERS, 0))
    monkeypatch.setattr(collector, "LAST_FORWARD", "NOT_OBSERVED")
    return key


@pytest.fixture
def downstream(monkeypatch):
    state = {"status": 200, "body": {}, "received": [], "redirect": None}
    class Receiver(BaseHTTPRequestHandler):
        def do_POST(self):
            state["received"].append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
            self.send_response(state["status"])
            self.send_header("Content-Type", "application/json")
            if state["redirect"]:
                self.send_header("Location", state["redirect"])
            self.end_headers()
            self.wfile.write(json.dumps(state["body"]).encode())
        def log_message(self, *_):
            pass
    server = ThreadingHTTPServer(("127.0.0.1", 0), Receiver)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setattr(collector, "FORWARD_ENDPOINT", f"http://127.0.0.1:{server.server_port}/v1/traces")
    try:
        yield state
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_real_delivery_carries_verifiable_complete_span_and_context(configured, downstream):
    original = payload()
    pristine = copy.deepcopy(original)
    with TestClient(collector.build_fastapi()) as client:
        response = client.post("/v1/traces", json=original)
        assert response.status_code == 200
        assert response.json()["szl"]["request"]["forwarded"] == 1
        assert response.json()["partialSuccess"] == {}
    assert original == pristine
    rs = downstream["received"][0]["resourceSpans"][0]
    span = rs["scopeSpans"][0]["spans"][0]
    attrs = {v["key"]: v["value"] for v in span["attributes"]}
    envelope = json.loads(attrs["szl.dsse.receipt"]["stringValue"])
    signed = base64.b64decode(envelope["payload"])
    configured.public_key().verify(base64.b64decode(envelope["signatures"][0]["sig"]),
                                   _pae(envelope["payloadType"], signed), ec.ECDSA(hashes.SHA256()))
    original_rs = pristine["resourceSpans"][0]
    original_span = original_rs["scopeSpans"][0]["spans"][0]
    bound = {"trace_id": original_span["traceId"], "span_id": original_span["spanId"],
             "name": original_span["name"], "span": original_span,
             "resource": original_rs["resource"], "scope": original_rs["scopeSpans"][0]["scope"]}
    digest = hashlib.sha256(json.dumps(bound, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert json.loads(signed)["subject"][0]["digest"]["sha256"] == digest
    assert attrs["szl.dsse.receipt_hash"]["stringValue"] == hashlib.sha256(signed).hexdigest()
    assert len(span["attributes"]) == len(attrs)  # no duplicate axis keys


def test_concurrent_deliveries_do_not_hold_global_state_lock(configured, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor

    monkeypatch.setattr(collector, "FORWARD_ENDPOINT", "http://127.0.0.1:4318/v1/traces")
    rendezvous = threading.Barrier(4)

    def forward(_batch):
        # All requests must reach downstream I/O together. The old global lock
        # broke this barrier before any other request could enter forwarding.
        rendezvous.wait(timeout=2)
        return 1

    monkeypatch.setattr(collector, "_forward", forward)
    raw = json.dumps(payload()).encode()
    with ThreadPoolExecutor(max_workers=4) as executor:
        responses = list(executor.map(lambda _: collector.trace_response(raw, "application/json"), range(4)))
    assert all(code == 200 and body["szl"]["request"]["forwarded"] == 1 for code, body in responses)
    assert collector.COUNTERS == {"received": 4, "accepted": 4, "rejected": 0, "forwarded": 4}


def test_rfc8785_subject_has_portable_unicode_float_and_sorting_vector():
    subject = {"trace_id": "a", "span_id": "b", "name": "é", "sample": 1e-7,
               "negative_zero": -0.0, "keys": {"\ue000": 2, "😀": 1}}
    # Independent fixed RFC 8785 vector: UTF-8 strings, UTF-16 key ordering,
    # ECMAScript number formatting, and negative zero normalized to zero.
    expected = '{"keys":{"😀":1,"\ue000":2},"name":"é","negative_zero":0,"sample":1e-7,"span_id":"b","trace_id":"a"}'.encode()
    statement = _in_toto_statement(subject, {"lambda_value": 0.97, "floor": 0.90,
                                           "passed": True, "axes": [0.97] * 5})
    assert statement["subject"][0]["digest"]["sha256"] == hashlib.sha256(expected).hexdigest()
    assert statement["predicate"]["subject_canonicalization"] == "RFC8785"
    assert statement["predicateType"].endswith("/v2")


@pytest.mark.parametrize("invalid", [float("nan"), float("inf"), 2 ** 60, "\ud800"])
def test_noncanonical_subject_values_rejected_before_signing(configured, downstream, invalid):
    body = payload()
    body["resourceSpans"][0]["resource"]["invalid"] = invalid
    code, _ = collector.trace_response(json.dumps(body).encode(), "application/json")
    assert code == 400 and downstream["received"] == []
    assert collector.COUNTERS["received"] == 0


def test_downstream_failure_is_retryable_and_not_forwarded(configured, downstream):
    downstream["status"] = 503
    with TestClient(collector.build_fastapi()) as client:
        assert client.post("/v1/traces", json=payload()).status_code == 503
        assert collector.COUNTERS["forwarded"] == 0
        downstream["status"] = 200
        result = client.post("/v1/traces", json=payload())
        assert result.status_code == 200
        assert result.json()["szl"]["request"]["forwarded"] == 1
        assert len(downstream["received"]) == 2


def test_downstream_partial_rejection_is_not_reported_as_delivery(configured, downstream):
    downstream["body"] = {"partialSuccess": {"rejectedSpans": "1", "errorMessage": "fixture rejection"}}
    with TestClient(collector.build_fastapi()) as client:
        response = client.post("/v1/traces", json=payload())
    assert response.status_code == 200
    assert response.json()["partialSuccess"]["rejectedSpans"] == "1"
    assert response.json()["szl"]["request"]["forwarded"] == 0


def test_gate_rejects_omitted_axis_without_forwarding(configured, downstream):
    data = payload()
    data["resourceSpans"][0]["scopeSpans"][0]["spans"][0]["attributes"].pop()
    with TestClient(collector.build_fastapi()) as client:
        response = client.post("/v1/traces", json=data)
    assert response.status_code == 200
    assert response.json()["partialSuccess"]["rejectedSpans"] == "1"
    assert downstream["received"] == []


@pytest.mark.parametrize("value", [None, True, "bad", float("nan"), float("inf"), -1, 2])
def test_unavailable_or_invalid_axis_never_passes(value):
    attrs = {f"lambda.a{i}": 0.97 for i in range(1, 6)}
    attrs["lambda.a1"] = value
    assert not lambda_gate.evaluate(attrs).passed


def test_default_local_signer_is_not_network_ready(monkeypatch, downstream):
    monkeypatch.delenv("VSP_SIGN_KEY_PEM", raising=False)
    monkeypatch.delenv("VSP_SIGN_MODE", raising=False)
    first, second = DsseSigner(), DsseSigner()
    assert first.keyid() != second.keyid()
    monkeypatch.setattr(collector, "SIGNER", first)
    with TestClient(collector.build_fastapi()) as client:
        assert client.get("/healthz").status_code == 200
        assert client.get("/readyz").status_code == 503
        assert client.post("/v1/traces", json=payload()).status_code == 503
    assert downstream["received"] == []


def test_missing_downstream_blocks_before_acceptance(configured, monkeypatch):
    monkeypatch.setattr(collector, "FORWARD_ENDPOINT", "")
    with TestClient(collector.build_fastapi()) as client:
        assert client.get("/readyz").status_code == 503
        assert client.post("/v1/traces", json=payload()).status_code == 503
    assert collector.COUNTERS["accepted"] == 0


@pytest.mark.parametrize("data", [[], {"resourceSpans": [None]}, {"resourceSpans": [{"scopeSpans": [1]}]}])
def test_malformed_shape_has_no_delivery(configured, downstream, data):
    with TestClient(collector.build_fastapi()) as client:
        assert client.post("/v1/traces", json=data).status_code == 400
    assert downstream["received"] == []


def test_content_type_size_and_reserved_attributes(configured, downstream):
    with TestClient(collector.build_fastapi()) as client:
        assert client.post("/v1/traces", content=b"{}", headers={"Content-Type": "application/x-protobuf"}).status_code == 415
        assert client.post("/v1/traces", content=b" " * (collector.MAX_REQUEST_BYTES + 1), headers={"Content-Type": "application/json"}).status_code == 413
        forged = payload()
        forged["resourceSpans"][0]["scopeSpans"][0]["spans"][0]["attributes"].append({"key": "szl.dsse.receipt", "value": {"stringValue": "forged"}})
        assert client.post("/v1/traces", json=forged).status_code == 400
    assert downstream["received"] == []


def test_unknown_signing_mode_fails_closed():
    with pytest.raises(ValueError, match="not implemented"):
        DsseSigner(mode="cosign")


def test_redirect_is_not_followed_and_proxies_are_ignored(configured, downstream, monkeypatch):
    downstream["status"] = 307
    downstream["redirect"] = collector.FORWARD_ENDPOINT + "?redirected"
    monkeypatch.setenv("HTTP_PROXY", "http://127.0.0.1:1")
    monkeypatch.setenv("http_proxy", "http://127.0.0.1:1")
    monkeypatch.setenv("NO_PROXY", "")
    monkeypatch.setenv("no_proxy", "")
    with TestClient(collector.build_fastapi()) as client:
        response = client.post("/v1/traces", json=payload())
    assert response.status_code == 503
    assert len(downstream["received"]) == 1
    assert collector.COUNTERS["forwarded"] == 0


@pytest.mark.parametrize("ack", [{"error": "rejected"}, {"partialSuccess": {"rejectedSpans": True}}, {"partialSuccess": {"rejectedSpans": 1.5}}])
def test_invalid_or_error_ack_is_not_delivery(configured, downstream, ack):
    downstream["body"] = ack
    with TestClient(collector.build_fastapi()) as client:
        response = client.post("/v1/traces", json=payload())
    assert response.status_code == 503
    assert collector.COUNTERS["forwarded"] == 0
