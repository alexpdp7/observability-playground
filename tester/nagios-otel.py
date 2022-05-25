"""
The default Nagios perfdata templates are:

host_perfdata_file_template
[HOSTPERFDATA]\t$TIMET$\t$HOSTNAME$\t$HOSTEXECUTIONTIME$\t$HOSTOUTPUT$\t$HOSTPERFDATA$
service_perfdata_file_template
[SERVICEPERFDATA]\t$TIMET$\t$HOSTNAME$\t$SERVICEDESC$\t$SERVICEEXECUTIONTIME$\t$SERVICELATENCY$\t$SERVICEOUTPUT$\t$SERVICEPERFDATA$

The pnp4nagios perfdata templates are:

service_perfdata_file_template
DATATYPE::SERVICEPERFDATA\tTIMET::$TIMET$\tHOSTNAME::$HOSTNAME$\tSERVICEDESC::$SERVICEDESC$\tSERVICEPERFDATA::$SERVICEPERFDATA$\tSERVICECHECKCOMMAND::$SERVICECHECKCOMMAND$\tHOSTSTATE::$HOSTSTATE$\tHOSTSTATETYPE::$HOSTSTATETYPE$\tSERVICESTATE::$SERVICESTATE$\tSERVICESTATETYPE::$SERVICESTATETYPE$

host_perfdata_file_template
DATATYPE::HOSTPERFDATA\tTIMET::$TIMET$\tHOSTNAME::$HOSTNAME$\tHOSTPERFDATA::$HOSTPERFDATA$\tHOSTCHECKCOMMAND::$HOSTCHECKCOMMAND$\tHOSTSTATE::$HOSTSTATE$\tHOSTSTATETYPE::$HOSTSTATETYPE$

And an example:

DATATYPE::HOSTPERFDATA	TIMET::1650828889	HOSTNAME::foo	HOSTPERFDATA::rta=126.113998ms;3000.000000;5000.000000;0.000000 pl=0%;80;100;0	HOSTCHECKCOMMAND::check-host-alive	HOSTSTATE::UP	HOSTSTATETYPE::HARD
DATATYPE::HOSTPERFDATA	TIMET::1650828889	HOSTNAME::bar	HOSTPERFDATA::rta=64.191002ms;3000.000000;5000.000000;0.000000 pl=0%;80;100;0	HOSTCHECKCOMMAND::check-host-alive	HOSTSTATE::UP	HOSTSTATETYPE::HARD
DATATYPE::HOSTPERFDATA	TIMET::1650828894	HOSTNAME::baz	HOSTPERFDATA::rta=64.448997ms;3000.000000;5000.000000;0.000000 pl=0%;80;100;0	HOSTCHECKCOMMAND::check-host-alive	HOSTSTATE::UP	HOSTSTATETYPE::HARD

DATATYPE::SERVICEPERFDATA	TIMET::1650828934	HOSTNAME::foo	SERVICEDESC::qux	SERVICEPERFDATA::time=0.127367s;;;0.000000;10.000000	SERVICECHECKCOMMAND::check_tcp!9982	HOSTSTATE::UP	HOSTSTATETYPE::HARD	SERVICESTATE::OK	SERVICESTATETYPE::HARD
DATATYPE::SERVICEPERFDATA	TIMET::1650828934	HOSTNAME::bar	SERVICEDESC::quux	SERVICEPERFDATA::time=0.189691s;;;0.000000 size=949B;;;0	SERVICECHECKCOMMAND::check_http!-H libreelec.bcn.int.pdp7.net -p 9981 -u /extjs.html -s Tvheadend	HOSTSTATE::UP	HOSTSTATETYPE::HARD	SERVICESTATE::OK	SERVICESTATETYPE::HARD
DATATYPE::SERVICEPERFDATA	TIMET::1650828938	HOSTNAME::baz	SERVICEDESC::foo	SERVICEPERFDATA::time=0.046059s;;;0.000000	SERVICECHECKCOMMAND::check_dns!-H maelcum.mad.int.pdp7.net -s $_HOSTPRIVATEIP$	HOSTSTATE::UPHOSTSTATETYPE::HARD	SERVICESTATE::OK	SERVICESTATETYPE::HARD
"""


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