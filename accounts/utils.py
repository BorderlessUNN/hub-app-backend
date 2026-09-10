import re

from helpers.exceptions import CustomValidationException


def normalize_phone_number(raw):
    """
    Normalize a Nigerian phone number to E.164 format (+234XXXXXXXXXX).

    Accepts, in any of these shapes, with or without spaces/dashes:
      - 0XXXXXXXXXX   (11 digits, leading 0)
      - 234XXXXXXXXXX (13 digits)
      - +234XXXXXXXXXX
      - XXXXXXXXXX    (10 digit local number, no leading 0)
    """
    if not raw:
        raise CustomValidationException(msg="Phone number is required", code=400)

    digits = re.sub(r"\D", "", str(raw))

    if digits.startswith("234") and len(digits) == 13:
        local = digits[3:]
    elif digits.startswith("0") and len(digits) == 11:
        local = digits[1:]
    elif len(digits) == 10:
        local = digits
    else:
        raise CustomValidationException(
            msg="Enter a valid Nigerian phone number (e.g. 08012345678)",
            code=400,
        )

    return f"+234{local}"
