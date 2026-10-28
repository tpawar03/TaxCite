"""Tracing (G1b): OpenTelemetry spans, exported to Langfuse Cloud over OTLP.

Off unless the Langfuse keys are set, and then every span is OpenTelemetry's no-op. When on,
export is batched on a background thread and a failed export is logged and dropped by the SDK,
so tracing can neither slow an answer nor fail one (the rule ADR-16 set for Redis).
"""

import base64
import json
import os

from opentelemetry import trace

tracer = trace.get_tracer("taxcite")
traced = tracer.start_as_current_span  # also a decorator: @traced("decompose") wraps every call in a span


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
