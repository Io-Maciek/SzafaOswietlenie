from typing import TextIO, Type

from ioDeSer._DeSer._IoDes import _IoDes as __IoDes__
from ioDeSer._DeSer._IoSer import _IoSer as __IoSer__


def write_to_file(obj: object, file: TextIO):
    """
    Converts the provided object to .io file format and writes it the provided file.

    Args:
        obj: The object to be converted.
        file: File to which the converted object will be serialized.

    Raises:
        TypeNotSupportedError: If 'obj' type is not supported.
    """
    file.write(write_to_string(obj))


def write_to_string(obj: object) -> str:
    """
    Converts the provided object to .io file format.

    Args:
        obj: The object to be converted.

    Raises:
        TypeNotSupportedError: If 'obj' type is not supported.

    Returns:
        Str in .io file format.
    """
    return __IoSer__.write(obj, 0)


def read_from_file(file: TextIO, object_type: Type, elements_type: Type = None) -> object:
    """
    Reads the content of provided file in .io file format and deserializes it to type 'object_type'.

    Args:
        file: File from which deserialized object will be read.
        object_type: The type of object that will be deserialized from 'ioStr'.
        elements_type: The type of objects inside lists or dictionaries.

    Raises:
        TypeNotImplementedError: If deserialization of provided type is not yet implemented in this version.
        ConstructorError: If provided type is a class without default constructor.
        FieldNotFoundError: If some deserialized field from 'ioStr' does not exist in provided class.

    Returns:
        Object of type 'object_type'.
    """
    return read_from_str(file.read(), object_type, elements_type)


def read_from_str(io_str: str, object_type: Type, elements_type: Type = None) -> object:
    """
    Reads the content of provided 'ioStr' string in .io file format and deserializes it to type 'object_type'.

    Args:
        io_str: Serialized object in .io file format.
        object_type: The type of object that will be deserialized from 'ioStr'.
        elements_type: The type of objects inside lists or dictionaries.

    Raises:
        TypeNotImplementedError: If deserialization of provided type is not yet implemented in this version.
        ConstructorError: If provided type is a class without default constructor.
        FieldNotFoundError: If some deserialized field from 'ioStr' does not exist in provided class.

    Returns:
        Object of type 'object_type'.
    """
    return __IoDes__.read(io_str, object_type, elements_type)
