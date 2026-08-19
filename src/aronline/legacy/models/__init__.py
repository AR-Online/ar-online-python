"""The shapes the legacy gateway answers.

They are ``TypedDict``s, like the /v3 models, and they carry the field names
**as the gateway writes them** -- ``dateSend``, ``customID``, ``criadoEm``. No
conversion layer sits in the middle: what you read in the SDK is what you see in
the gateway's documentation and in our support records.

Two conventions the wire distinguishes, so the types distinguish them too: a key
that comes ``null`` is typed ``| None``, and a key that simply vanishes from the
response is a non-required key of a ``total=False`` block.
"""

from aronline.legacy.models.envio import (
    SMS_TYPE_SENDS,
    Anexo,
    CanalCarta,
    CanalSms,
    CanalVoz,
    CanalWhatsapp,
    EnvioRequest,
    EnvioResponse,
    EnvioValidation,
    SmsTypeSend,
)
from aronline.legacy.models.full import (
    FullChannelDetail,
    StatusEvent,
    StatusFull,
    StatusHistory,
    StatusLast,
)
from aronline.legacy.models.gw_template import (
    GW_TEMPLATE_TYPES,
    GwTemplate,
    GwTemplateType,
    GwTemplateWriteResult,
    UpdateGwTemplate,
)
from aronline.legacy.models.regua import FinalizarReguaResult
from aronline.legacy.models.sending_proof import SendingProof
from aronline.legacy.models.status import (
    SmsAnswer,
    StatusCarta,
    StatusEmail,
    StatusSms,
    StatusVoz,
    StatusWhatsapp,
)
from aronline.legacy.models.webhook import (
    WebhookChannel,
    WebhookMetadata,
    WebhookPayloadV1,
    WebhookPayloadV2,
    WebhookStatusPayload,
)

__all__ = [
    "GW_TEMPLATE_TYPES",
    "SMS_TYPE_SENDS",
    "Anexo",
    "CanalCarta",
    "CanalSms",
    "CanalVoz",
    "CanalWhatsapp",
    "EnvioRequest",
    "EnvioResponse",
    "EnvioValidation",
    "FinalizarReguaResult",
    "FullChannelDetail",
    "GwTemplate",
    "GwTemplateType",
    "GwTemplateWriteResult",
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
    "UpdateGwTemplate",
    "WebhookChannel",
    "WebhookMetadata",
    "WebhookPayloadV1",
    "WebhookPayloadV2",
    "WebhookStatusPayload",
]
