def logger(**kwargs):
    pass


def split_headers(headers):
    h_dict = dict()
    # print("headers to split:", headers)
    for header in headers:
        splitted = header.split(":", 1)
        # print("splitted: ", splitted)
        h_dict[splitted[0]] = splitted[1].strip()
    # for header in headers
    return h_dict


def construct_headers(headers_dict):
    dict_list = list()
    for key, value in headers_dict.items():
        temp = '{name}: {value}'.format(name=key, value=value)
        dict_list.append(temp)

    header_string = str.join("\r\n", dict_list)
    return header_string


def split_params(params):
    p_dict = dict()
    if params.count("&") > 0:
        params = params.split("&")
        for param in params:
            splitted = param.split("=")
            p_dict[splitted[0]] = splitted[1]
    else:
        splitted = params.split("=")
        p_dict[splitted[0]] = splitted[1]
    return p_dict


def has_query_params(route) -> bool:
    if route.count("?") > 0:
        return True
    return False


def split_route_without_query(route):
    '''
    :param route:
    :return:
    [0] -> route
    [1] -> id
    '''
    route_and_params = [x for x in route.split("/") if len(x) is not 0]
    if len(route_and_params) > 1:
        return route_and_params
    else:
        return [route_and_params[0], '']


def split_route_with_query(route):
    '''
    :param route:
    :return:
    [0] -> route
    [1] -> id
    '''
    return [x for x in route.split("/") if len(x) is not 0][0].split("?")
