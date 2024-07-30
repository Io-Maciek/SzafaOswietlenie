from typing import Type


class FieldNotFoundError(Exception):
    def __init__(self, object_type: Type, field_name: str):
        super().__init__(f"Object of type {object_type} does not have field named '{field_name}'. It might be an error "
                         f"in __io__ method.")


class ConstructorError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

