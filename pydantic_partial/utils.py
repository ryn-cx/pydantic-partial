from typing import Any, no_type_check

import pydantic
from pydantic.fields import FieldInfo

from pydantic_partial import _compat


@no_type_check
def copy_field_info(field_info: FieldInfo, **overrides: Any) -> FieldInfo:
    """
    Return a copy of a pydantic FieldInfo object, allow to override
    certain values.
    """

    if _compat.PYDANTIC_V2 and "json_schema_extra" in overrides and field_info.json_schema_extra:
        overrides = overrides.copy()
        overrides["json_schema_extra"] = {
            **field_info.json_schema_extra,
            **overrides["json_schema_extra"],
        }

    field = pydantic.Field(
        **{
            **{k: v for k, v in field_info.__repr_args__() if k not in ("extra", "annotation", "required")},
            **(field_info.extra if _compat.PYDANTIC_V1 else {}),
            **overrides,
        },
    )

    # Manually add back field validation because pydantic.Field does not support
    # it during model creation.
    if _compat.PYDANTIC_V2:
        from pydantic import AfterValidator, BeforeValidator, PlainValidator, WrapValidator
        for k in field_info.metadata:
            if isinstance(k, (BeforeValidator, AfterValidator, PlainValidator, WrapValidator)):
                field.metadata.append(k)

    return field
