import sentry_sdk
from app.config.common import settings


def init_sentry():
    sentry_sdk.init(
        settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        release=settings.RELEASE_VERSION,
        # TODO: check
        # attach_stacktrace=True,
        # integrations=[
        #     LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
        #     GnuBacktraceIntegration(),
        #     StarletteIntegration(
        #         transaction_style="endpoint",
        #         failed_request_status_codes={403, *range(500, 599)},
        #         http_methods_to_capture=("GET",),
        #     ),
        #     FastApiIntegration(
        #         transaction_style="endpoint",
        #         failed_request_status_codes={403, *range(500, 599)},
        #         http_methods_to_capture=("GET",),
        #     ),
        # ],
        # # Set traces_sample_rate to 1.0 to capture 100% of transactions for tracing.
        # traces_sample_rate=1.0,
        # # Set profiles_sample_rate to 1.0 to profile 100% of sampled transactions.
        # # We recommend adjusting this value in production.
        # profiles_sample_rate=1.0,
    )
