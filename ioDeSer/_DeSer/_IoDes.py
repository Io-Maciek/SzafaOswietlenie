from collections import abc

from ioDeSer.ioDeSeriable import IoDeSerable
from ioDeSer.Errors.TypeErrors import *
from ioDeSer.Errors.ClassErrors import *


class _IoDes:
    @staticmethod
    def read(ioStr, objType, elements_type=None):
        ioStr = _IoDes.__substring_brackets(ioStr)
        primitive = (int, str, bool, float)
        if objType in primitive:
            if objType is bool:
                obj = ioStr == 'True' or ioStr == 'true'
            else:
                obj = objType(ioStr)
        elif objType is tuple:
            raise TypeNotSupportedError(tuple)
        elif issubclass(objType, abc.Sequence):
            if elements_type is None:
                raise Exception("You have to pass type of elements in sequence using 'elements_type'.")
            ioStr = _IoDes.__delete_tabs(ioStr)
            lines = ioStr.split('\n+\n')
            obj = objType()

            for i in range(len(lines)):
                new_el = _IoDes.read(lines[i], elements_type)
                if hasattr(obj, "append"):
                    obj.append(new_el)
                else:
                    # obj = objType(obj + objType(new_el))
                    raise NotImplementedError(f"{objType} not implemented yet.")
        elif objType is dict:
            ioStr = _IoDes.__delete_tabs(ioStr)
            lines = ioStr.split('\n+\n')
            obj = {}
            for k in elements_type:
                key_type = k
                value_type = elements_type[k]
                break

            for i in range(len(lines)):
                io_dict = _IoDes.__delete_tabs(lines[i][1:-1])
                lines2 = io_dict.split('\n+\n')
                key = _IoDes.read(lines2[0], key_type)
                value = _IoDes.read(lines2[1], value_type)
                obj[key] = value

        elif issubclass(objType, IoDeSerable):
            try:
                obj = objType()
            except TypeError as e:
                raise ConstructorError(
                    f"Object of type {objType} must have parameterless constructor or with default values.")

            ioStr = _IoDes.__delete_tabs(ioStr)
            lines = ioStr.split('\n')

            var_types = objType.__io__()

            for l in range(len(lines)):  # TODO fix lines meaby?
                assignments = lines[l].split('->')
                var_name = assignments[0].strip()
                found_field = None

                for field in var_types:
                    if var_name == field:
                        found_field = field
                        break
                if found_field is not None:
                    if var_types[found_field] in primitive:
                        val = _IoDes.read(assignments[1].strip(), var_types[found_field])
                        setattr(obj, found_field, val)
                    else:
                        # TODO add deserialization of classes
                        l = l + 1
                        new_object_start = l
                        while lines[l] != "|":
                            l = l + 1

                        new_object_end = l
                        new_object_string = "|\n"

                        for l2 in range(new_object_start, new_object_end):
                            new_object_string += lines[l2] + "\n"
                        new_object_string += "|"  # TODO is was "\n|"?

                        elements_type = None
                        passed_type = var_types[found_field]

                        if isinstance(var_types[found_field], abc.Sequence):
                            elements_type = var_types[found_field][0]
                            passed_type = type(var_types[found_field])

                        elif isinstance(var_types[found_field], dict):
                            passed_type = type(var_types[found_field])
                            elements_type = var_types[found_field]

                        val = _IoDes.read(new_object_string.strip(), passed_type, elements_type)
                        setattr(obj, found_field, val)

                    del var_types[found_field]
        else:
            raise TypeNotSupportedError(objType)
        return obj

    @staticmethod
    def __substring_brackets(ioString):
        firstIndex = -1
        lastIndex = -1
        for i in range(len(ioString)):
            if ioString[i] == '|':
                firstIndex = i + 1
                break
        for i in range(len(ioString)):
            if ioString[len(ioString) - 1 - i] == '|':
                lastIndex = len(ioString) - 1 - i
                break
        ioString = ioString[firstIndex:lastIndex]
        return ioString

    @staticmethod
    def __delete_tabs(input_str):
        ret = ""
        lines = input_str.split('\n')
        for i in range(len(lines)):
            ret += (lines[i])[1:] + "\n"
        return ret.strip()
