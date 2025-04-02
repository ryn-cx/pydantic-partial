from typing import Annotated, Any

import pydantic
import pytest

from pydantic_partial import create_partial_model
from pydantic_partial import _compat
from pydantic import BaseModel, ValidationError, field_validator
from typing import Any

from typing import Annotated

from pydantic import BaseModel, Field, ValidationError, ValidatorFunctionWrapHandler, field_validator


class TestDecorators:
    def test_after(self):
        class Model(BaseModel):
            number: int

            @field_validator("number", mode="after")
            @classmethod
            def is_even(cls, value: int) -> int:
                if value % 2 == 1:
                    raise ValueError(f"{value} is not an even number")
                return value

        PartialModel = create_partial_model(Model)

        with pytest.raises(ValidationError):
            PartialModel(number=1)

        model = PartialModel(number=2)
        assert model.model_dump(exclude_unset=True) == {"number": 2}

    def test_before(self):
        class Model(BaseModel):
            numbers: list[int]

            @field_validator("numbers", mode="before")
            @classmethod
            def ensure_list(cls, value: Any) -> Any:
                if not isinstance(value, list):
                    return [value]
                else:
                    return value

        PartialModel = create_partial_model(Model)

        with pytest.raises(ValidationError):
            PartialModel(numbers="str")

        model = PartialModel(numbers=2)
        assert model.model_dump(exclude_unset=True) == {"numbers": [2]}

    def test_plain(self):
        class Model(BaseModel):
            number: int

            @field_validator("number", mode="plain")
            @classmethod
            def val_number(cls, value: Any) -> Any:
                if isinstance(value, int):
                    return value * 2
                else:
                    return value

        PartialModel = create_partial_model(Model)

        model = PartialModel(number=4)
        assert model.model_dump(exclude_unset=True) == {"number": 8}

        model = PartialModel(number="invalid")
        assert model.model_dump(exclude_unset=True) == {"number": "invalid"}

    # def test_wrap(self):
    #     class Model(BaseModel):
    #         my_string: Annotated[str, Field(max_length=5)]

    #         @field_validator("my_string", mode="wrap")
    #         @classmethod
    #         def truncate(cls, value: Any, handler: ValidatorFunctionWrapHandler) -> str:
    #             try:
    #                 return handler(value)
    #             except ValidationError as err:
    #                 if err.errors()[0]["type"] == "string_too_long":
    #                     return handler(value[:5])
    #                 else:
    #                     raise

    #     PartialModel = create_partial_model(Model)

    #     model = PartialModel(my_string="abcde")
    #     assert model.model_dump(exclude_unset=True) == {"my_string": "abcde"}

    #     model = PartialModel(my_string="abcdef")
    #     assert model.model_dump(exclude_unset=True) == {"my_string": "abcde"}


class TestAnnotated:
    if _compat.PYDANTIC_V2:

        def test_after(self):
            from pydantic import AfterValidator

            def is_even(value: int) -> int:
                if value % 2 == 1:
                    raise ValueError(f"{value} is not an even number")
                return value

            class Model(BaseModel):
                number: Annotated[int, AfterValidator(is_even)]

            PartialModel = create_partial_model(Model)

            with pytest.raises(ValidationError):
                PartialModel(number=1)

            model = PartialModel(number=2)
            assert model.model_dump(exclude_unset=True) == {"number": 2}

        def test_before(self):
            from pydantic import BeforeValidator

            def ensure_list(value: Any) -> Any:
                if not isinstance(value, list):
                    return [value]
                else:
                    return value

            class Model(BaseModel):
                numbers: Annotated[list[int], BeforeValidator(ensure_list)]

            PartialModel = create_partial_model(Model)

            with pytest.raises(ValidationError):
                PartialModel(numbers="str")

            model = PartialModel(numbers=2)
            assert model.model_dump(exclude_unset=True) == {"numbers": [2]}

        def test_plain(self):
            from pydantic import PlainValidator

            def val_number(value: Any) -> Any:
                if isinstance(value, int):
                    return value * 2
                else:
                    return value

            class Model(BaseModel):
                number: Annotated[int, PlainValidator(val_number)]

            PartialModel = create_partial_model(Model)

            model = PartialModel(number=4)
            assert model.model_dump(exclude_unset=True) == {"number": 8}

            model = PartialModel(number="invalid")
            assert model.model_dump(exclude_unset=True) == {"number": "invalid"}

        # def test_wrap(self):
        #     from pydantic import WrapValidator

        #     def truncate(value: Any, handler: ValidatorFunctionWrapHandler) -> str:
        #         try:
        #             return handler(value)
        #         except ValidationError as err:
        #             if err.errors()[0]["type"] == "string_too_long":
        #                 return handler(value[:5])
        #             else:
        #                 raise

        #     class Model(BaseModel):
        #         my_string: Annotated[str, Field(max_length=5), WrapValidator(truncate)]

        #     PartialModel = create_partial_model(Model)

        #     model = PartialModel(my_string="abcde")
        #     assert model.model_dump(exclude_unset=True) == {"my_string": "abcde"}

        #     model = PartialModel(my_string="abcdef")
        #     assert model.model_dump(exclude_unset=True) == {"my_string": "abcde"}
