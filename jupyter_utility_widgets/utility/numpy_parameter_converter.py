from typing import List, Literal, Callable
from ipywidgets import IntText, FloatText, Checkbox, Box
from numpydoc.docscrape import NumpyDocString, Parameter
from warnings import warn

"""
NOTE: This is an exremely early prototype of the feature and is missing A LOT of possible options
e.g.:
* Types
* Parsing of the "type" section
* Automation of func->widget
etc
"""

known_types = {
    "int": int,
    "float": float,
    "bool": bool
}

type_text_widget = {
    int: IntText,
    float: FloatText,
    bool: Checkbox
}

SKIP_PARAMETER = 0

class NumpyFunctionUIFactory:
    @staticmethod
    def get_parameter_types(func: Callable):
        parsed = NumpyDocString(func.__doc__)
        parameters: List[Parameter] = parsed["Parameters"]
        return parameters, {parameter.name: known_types.get(parameter.type) for parameter in parameters}

    @staticmethod
    def construct_widgets(parameters: List[Parameter], parameter_types=None):
        if parameter_types is None:
            parameter_types = NumpyFunctionUIFactory.get_parameter_types(parameters)

        widgets = []
        for parameter in parameters:
            current_type = parameter_types.get(parameter.name)
            
            if current_type is None:
                if "optional" not in parameter.type:
                    warn("Missing type '%s' for non-optional parameter %s" % (parameter.type, parameter.name))
                continue
            
            if current_type == SKIP_PARAMETER:
                continue

            widgets.append(type_text_widget[current_type](description=parameter.name))
        
        return widgets
            
