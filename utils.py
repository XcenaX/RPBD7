def get_or_none(request, parameter, value_if_none=None):
    try:
        return request.args.get(parameter, "")
    except:
        return value_if_none

def post_or_none(request, parameter, value_if_none=None):
    try:
        return request.POST[parameter]
    except:
        return value_if_none

def parameter_or_none(parameter):
    try:
        return parameter
    except:
        ""