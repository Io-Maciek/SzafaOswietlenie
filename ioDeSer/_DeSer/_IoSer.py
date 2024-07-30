import collections.abc

from ioDeSer.ioDeSeriable import IoDeSerable
from ioDeSer.Errors.ClassErrors import FieldNotFoundError
from ioDeSer.Errors.TypeErrors import *


class _IoSer:
    @staticmethod
    def __add_shift(shift) -> str:
        ret = ""
        for x in range(shift):
            ret += "\t"
        return ret

    @staticmethod
    def write(obj, shift_number) -> str:
        primitive = (int, str, bool, float)
        ret = ""

        if isinstance(obj, primitive):
            ret = "|" + str(obj) + "|"
        elif isinstance(obj, collections.abc.Sequence):
            arrayRet = ""
            for i in range(len(obj)):
                arrayRet += _IoSer.__add_shift(shift_number + 1) + _IoSer.write(obj[i], shift_number + 1)
                if i < len(obj) - 1:
                    arrayRet += "\n" + _IoSer.__add_shift(shift_number + 1) + "+\n"
            ret = "|\n" + arrayRet + "\n" + _IoSer.__add_shift(shift_number) + "|"
        elif isinstance(obj, dict):  # TODO dictionary serialization
            arrayRet = ""
            is_first = True
            for key in obj:
                value = obj[key]
                if not is_first:
                    arrayRet += f"\n{_IoSer.__add_shift(shift_number + 1)}+\n"
                else:
                    is_first = False

                arrayRet += f"{_IoSer.__add_shift(shift_number + 1)}|" \
                            f"\n{_IoSer.__add_shift(shift_number + 2)}{_IoSer.write(key, shift_number + 1)}" \
                            f"\n{_IoSer.__add_shift(shift_number + 2)}+" \
                            f"\n{_IoSer.__add_shift(shift_number + 2)}{_IoSer.write(value, shift_number + 2)}" \
                            f"\n{_IoSer.__add_shift(shift_number + 1)}|"
                # TODO /\

            ret = "|\n" + arrayRet + "\n" + _IoSer.__add_shift(shift_number) + "|"
        elif issubclass(type(obj), IoDeSerable):  # inspect.isclass(type(obj)):
            class_ret = ""
            first = True

            var_types = type(obj).__io__()
            for v in var_types:
                try:
                    value = getattr(obj, v)
                    if not first:
                        class_ret += "\n"
                    first = False
                    class_ret += _IoSer.__add_shift(shift_number + 1) + v + "->" + _IoSer.write(value,
                                                                                              shift_number + 1)
                except AttributeError:
                    raise FieldNotFoundError(type(obj), v)

            ret = "|\n" + class_ret + "\n" + _IoSer.__add_shift(shift_number) + "|"
        else:
            raise TypeNotSupportedError(type(obj))

        return ret
