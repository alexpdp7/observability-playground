from opentelemetry import _metrics

from opentelemetry.sdk import _metrics as sdk_metrics
from opentelemetry.sdk._metrics import export

from opentelemetry.exporter.otlp.proto.grpc import _metric_exporter


exporter = _metric_exporter.OTLPMetricExporter()
reader = export.PeriodicExportingMetricReader(exporter)
provider = sdk_metrics.MeterProvider(metric_readers=[reader])
_metrics.set_meter_provider(provider)

meter = _metrics.get_meter_provider().get_meter("getting-started", "0.1.2")

# Counter
counter = meter.create_counter("counter")
counter.add(1)
