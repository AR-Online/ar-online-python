"""Official SDK for the AR Online API.

The SDK speaks two surfaces. The /v3 resources at the top of ``Client`` are the
clean contract. ``client.legacy`` speaks the old gateway exactly as its public
documentation describes it -- idiosyncrasies included -- because an integration
written against the old API needs typed calls today, and normalizing the old
contract would break the callers the area exists to keep working.

The /v1 and /v2 mirrors are not covered: they answer the old contracts byte for
byte, and a typed client that "improved" them would break the same callers.
"""

from aronline.client import Client
from aronline.errors import ApiError, ErrorDetail
from aronline.http.transport import DEFAULT_BASE_URL, DEFAULT_TIMEOUT
from aronline.legacy.area import LegacyArea
from aronline.legacy.errors import LegacyApiError
from aronline.legacy.models import (
    GW_TEMPLATE_TYPES,
    SMS_TYPE_SENDS,
    Anexo,
    CanalCarta,
    CanalSms,
    CanalVoz,
    CanalWhatsapp,
    EnvioRequest,
    EnvioResponse,
    EnvioValidation,
    FinalizarReguaResult,
    FullChannelDetail,
    GwTemplate,
    GwTemplateType,
    GwTemplateWriteResult,
    SendingProof,
    SmsAnswer,
    SmsTypeSend,
    StatusCarta,
    StatusEmail,
    StatusEvent,
    StatusFull,
    StatusHistory,
    StatusLast,
    StatusSms,
    StatusVoz,
    StatusWhatsapp,
    UpdateGwTemplate,
    WebhookChannel,
    WebhookMetadata,
    WebhookPayloadV1,
    WebhookPayloadV2,
    WebhookStatusPayload,
)
from aronline.legacy.transport import DEFAULT_LEGACY_BASE_URL
from aronline.models import (
    CHANNELS,
    AllowlistEntry,
    Channel,
    Freshness,
    Tag,
    Template,
    TemplateVariable,
    Version,
)

#: This package's version -- the same string ``pyproject.toml`` carries.
VERSION = "0.3.0"

__all__ = [
    "CHANNELS",
    "DEFAULT_BASE_URL",
    "DEFAULT_LEGACY_BASE_URL",
    "DEFAULT_TIMEOUT",
    "GW_TEMPLATE_TYPES",
    "SMS_TYPE_SENDS",
    "VERSION",
    "AllowlistEntry",
    "Anexo",
    "ApiError",
    "CanalCarta",
    "CanalSms",
    "CanalVoz",
    "CanalWhatsapp",
    "Channel",
    "Client",
    "EnvioRequest",
    "EnvioResponse",
    "EnvioValidation",
    "ErrorDetail",
    "FinalizarReguaResult",
    "Freshness",
    "FullChannelDetail",
    "GwTemplate",
    "GwTemplateType",
    "GwTemplateWriteResult",
    "LegacyApiError",
    "LegacyArea",
    "SendingProof",
    "SmsAnswer",
    "SmsTypeSend",
    "StatusCarta",
    "StatusEmail",
    "StatusEvent",
    "StatusFull",
    "StatusHistory",
    "StatusLast",
    "StatusSms",
    "StatusVoz",
    "StatusWhatsapp",
    "Tag",
    "Template",
    "TemplateVariable",
    "UpdateGwTemplate",
    "Version",
    "WebhookChannel",
    "WebhookMetadata",
    "WebhookPayloadV1",
    "WebhookPayloadV2",
    "WebhookStatusPayload",
]
