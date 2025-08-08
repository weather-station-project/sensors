import logging

from opentelemetry import trace, metrics
from opentelemetry._logs import set_logger_provider, get_logger
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs._internal.export import BatchLogRecordProcessor, ConsoleLogExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics._internal.export import MetricExporter
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION, DEPLOYMENT_ENVIRONMENT
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from src.config.global_config import global_config


# Useful links
#  https://opentelemetry.io/docs/languages/python/
#  https://opentelemetry.io/docs/concepts/semantic-conventions/
#  https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation#readme


def get_processor() -> BatchSpanProcessor:
    if global_config.otel.debug_in_console:
        return BatchSpanProcessor(ConsoleSpanExporter())

    return BatchSpanProcessor(span_exporter=OTLPSpanExporter(endpoint=f"{global_config.otel.root_url}/v1/traces"))


def get_metric_exporter() -> MetricExporter:
    if global_config.otel.debug_in_console:
        return ConsoleMetricExporter()

    return OTLPMetricExporter(endpoint=f"{global_config.otel.root_url}/v1/metrics")


resources: Resource = Resource.create(
    attributes={
        SERVICE_NAME: global_config.otel.attrs[SERVICE_NAME],
        SERVICE_VERSION: global_config.otel.attrs[SERVICE_VERSION],
        DEPLOYMENT_ENVIRONMENT: global_config.otel.attrs[DEPLOYMENT_ENVIRONMENT],
    }
)

tracer_provider = TracerProvider(resource=resources)
tracer_provider.add_span_processor(span_processor=get_processor())
trace.set_tracer_provider(tracer_provider)

metric_reader = PeriodicExportingMetricReader(exporter=get_metric_exporter())
meter_provider = MeterProvider(resource=resources, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider=meter_provider)

# xxx
provider = LoggerProvider()
processor = BatchLogRecordProcessor(ConsoleLogExporter())
provider.add_log_record_processor(processor)
# Sets the global default logger provider
set_logger_provider(provider)

logger = get_logger(__name__)

handler = LoggingHandler(level=logging.INFO, logger_provider=provider)
logging.basicConfig(handlers=[handler], level=logging.INFO)

logging.info("This is an OpenTelemetry log record!")
