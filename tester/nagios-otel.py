from opentelemetry import _metrics

from opentelemetry.sdk import _metrics as sdk_metrics
from opentelemetry.sdk._metrics import export
from opentelemetry._metrics import observation
from opentelemetry.exporter.otlp.proto.grpc import _metric_exporter


exporter = _metric_exporter.OTLPMetricExporter()
reader = export.PeriodicExportingMetricReader(exporter)
provider = sdk_metrics.MeterProvider(metric_readers=[reader])
_metrics.set_meter_provider(provider)

def _callback():
    yield observation.Observation(9, {'baz': 'qux'})

mp = _metrics.get_meter_provider()
m = m = mp.get_meter("foo")
g = m.create_observable_gauge("bar", callbacks=[_callback])
g.callback()


from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Resource can be required for some backends, e.g. Jaeger
# If resource wouldn't be set - traces wouldn't appears in Jaeger
resource = Resource(attributes={
    "service.name": "service"
})

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

otlp_exporter = OTLPSpanExporter()

span_processor = BatchSpanProcessor(otlp_exporter)

trace.get_tracer_provider().add_span_processor(span_processor)

with tracer.start_as_current_span("foo"):
    print("Hello world!")