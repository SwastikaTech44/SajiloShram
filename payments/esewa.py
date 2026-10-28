import base64
import hashlib
import hmac
import json
import uuid
from decimal import Decimal, InvalidOperation

from django.conf import settings


class EsewaError(Exception):
    """Raised when an eSewa response is missing, unreadable or not trustworthy."""


def sign(message):
    digest = hmac.new(
        settings.ESEWA_SECRET_KEY.encode(),
        message.encode(),
        hashlib.sha256,
    ).digest()
    return base64.b64encode(digest).decode()


def build_payment_form(txn, success_url, failure_url):
    total = str(txn.amount)
    transaction_uuid = f"SJ-{txn.pk}-{uuid.uuid4().hex[:8]}"
    product_code = settings.ESEWA_PRODUCT_CODE

    message = (
        f"total_amount={total},"
        f"transaction_uuid={transaction_uuid},"
        f"product_code={product_code}"
    )

    fields = {
        "amount": total,
        "tax_amount": "0",
        "product_service_charge": "0",
        "product_delivery_charge": "0",
        "total_amount": total,
        "transaction_uuid": transaction_uuid,
        "product_code": product_code,
        "success_url": success_url,
        "failure_url": failure_url,
        "signed_field_names": "total_amount,transaction_uuid,product_code",
        "signature": sign(message),
    }
    return {"action_url": settings.ESEWA_FORM_URL, "fields": fields}


def decode_and_verify(encoded):
    encoded = encoded.replace(" ", "+")
    encoded += "=" * (-len(encoded) % 4)
    try:
        data = json.loads(base64.b64decode(encoded))
    except ValueError:
        raise EsewaError("Could not read the eSewa response.")

    names = str(data.get("signed_field_names", "")).split(",")
    for needed in ("status", "total_amount", "transaction_uuid", "product_code"):
        if needed not in names:
            raise EsewaError("The eSewa response is missing required fields.")

    try:
        message = ",".join(f"{name}={data[name]}" for name in names)
    except KeyError:
        raise EsewaError("The eSewa response is incomplete.")

    expected = sign(message).encode()
    received = str(data.get("signature", "")).encode()
    if not hmac.compare_digest(expected, received):
        raise EsewaError("The eSewa response signature is not valid.")
    return data


def txn_id_from_uuid(transaction_uuid):
    parts = str(transaction_uuid).split("-")
    if len(parts) == 3 and parts[0] == "SJ" and parts[1].isdigit():
        return int(parts[1])
    raise EsewaError("Unknown transaction reference.")


def to_decimal(value):
    try:
        return Decimal(str(value).replace(",", ""))
    except InvalidOperation:
        raise EsewaError("The paid amount could not be read.")