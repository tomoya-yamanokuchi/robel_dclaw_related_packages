from typing import TypedDict, get_type_hints, Any, Type



def check_typed_dict(data: dict, typed_dict: Type[TypedDict]) -> None:
    hints = get_type_hints(typed_dict)
    for key, expected_type in hints.items():
        if key not in data:
            raise TypeError(f"Missing key '{key}' in {typed_dict.__name__}")
        if not isinstance(data[key], expected_type):
            raise TypeError(f"Key '{key}' is expected to be of type {expected_type}, but got {type(data[key])} instead")
