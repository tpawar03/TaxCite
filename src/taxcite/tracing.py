"""Tracing (G1b): OpenTelemetry spans, exported to Langfuse Cloud over OTLP.

Off unless the Langfuse keys are set, and then every span is OpenTelemetry's no-op. When on,
export is batched on a background thread and a failed export is logged and dropped by the SDK,
so tracing can neither slow an answer nor fail one (the rule ADR-16 set for Redis).
"""

import base64
import dataclasses
import functools
import inspect
import json
import os

from opentelemetry import trace

tracer = trace.get_tracer("taxcite")


def traced(name: str, io: bool = True):
    """A span around every call. With `io`, the arguments passed and the result are the span's input and
    output in Langfuse; `call_model` sets its own (`generation`), so it turns this off."""
    def wrap(fn):
        signature = inspect.signature(fn)

        @functools.wraps(fn)
        def inner(*args, **kwargs):
            with tracer.start_as_current_span(name) as span:
                if io and span.is_recording():
                    span.set_attribute("langfuse.observation.input",
                                       _json(signature.bind(*args, **kwargs).arguments))
                result = fn(*args, **kwargs)
                if io and result is not None and span.is_recording():
                    span.set_attribute("langfuse.observation.output", _json(result))
                return result
        return inner
    return wrap


def _brief(x, depth: int = 0):
    """A readable, bounded copy of a step's arguments or result."""
    if isinstance(x, str):
        return x if len(x) <= 1000 else x[:1000] + "…"
    if x is None or isinstance(x, (int, float, bool)):
        return x
    if depth > 4:
        return "…"
    if dataclasses.is_dataclass(x) and not isinstance(x, type):
        if hasattr(x, "citation") and hasattr(x, "score"):  # a retrieved chunk: the llm span shows its text
            return {"citation": x.citation, "score": round(x.score, 4)}
        return {f.name: _brief(getattr(x, f.name), depth + 1) for f in dataclasses.fields(x)}
    if isinstance(x, dict):
        return {str(k): _brief(v, depth + 1) for k, v in x.items()}
    if isinstance(x, (list, tuple, set, frozenset)):
        items = [_brief(v, depth + 1) for v in list(x)[:50]]
        return items + [f"… {len(x) - 50} more"] if len(x) > 50 else items
    return f"<{type(x).__name__}>"  # a connection, a client: never its repr


def _json(x) -> str:
    return json.dumps(_brief(x), default=str)


def setup() -> bool:
    """Send spans to Langfuse if its keys are in the environment. Called once, by the API and by `--trace`."""
    public, secret = os.environ.get("LANGFUSE_PUBLIC_KEY"), os.environ.get("LANGFUSE_SECRET_KEY")
    if not (public and secret):
        return False
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    base = os.environ.get("LANGFUSE_BASE_URL", "https://cloud.langfuse.com").rstrip("/")
    auth = base64.b64encode(f"{public}:{secret}".encode()).decode()
    provider = TracerProvider(resource=Resource.create({"service.name": "taxcite"}))
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(
        endpoint=f"{base}/api/public/otel/v1/traces", headers={"Authorization": f"Basic {auth}"})))
    trace.set_tracer_provider(provider)
    return True


def annotate(attributes: dict) -> None:
    """Attributes on the current span; None values are left out. A no-op when tracing is off."""
    trace.get_current_span().set_attributes({k: v for k, v in attributes.items() if v is not None})


def generation(model: str, system: str, prompt: str, text: str, input_tokens: int, output_tokens: int,
               usd: float) -> None:
    """Mark the current span as one LLM call, in the attribute names Langfuse reads."""
    annotate({
        "langfuse.observation.type": "generation",
        "langfuse.observation.model.name": model,
        "langfuse.observation.input": json.dumps([{"role": "system", "content": system},
                                                  {"role": "user", "content": prompt}]),
        "langfuse.observation.output": text,
        "langfuse.observation.usage_details": json.dumps({"input": input_tokens, "output": output_tokens}),
        "langfuse.observation.cost_details": json.dumps({"total": usd}),
    })


def trace_id() -> str | None:
    """The current trace's id, as Langfuse shows it; None when tracing is off."""
    context = trace.get_current_span().get_span_context()
    return format(context.trace_id, "032x") if context.is_valid else None
