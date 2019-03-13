import json
import time
import config
import db_driver
import helpers


#from cachetools import cached, TTLCache  # 1 - let's import the "cached" decorator and the "TTLCache" object from cachetools
#cache = TTLCache(maxsize=100, ttl=300)  # 2 - let's create the cache object.
class HDict(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))


def handle_new_client(connection, address):
    request = connection.recv(1024)  # ?size
    print("request: ", request)
    startTime = time.time()
    with open("logging.txt", "a") as log:
        log.write("request: {request}\nstartTime: {startTime}\n".format(request=request, startTime=startTime))
    req, body = request.decode().split("\r\n\r\n")
    request_list = req.split("\r\n")
    method, route, protocol = request_list[0].split()
    headers = request_list[1:]
    headers = helpers.split_headers(headers)  # 2 blank lines at the end
    # headers = str.join("\r\n", headers)
    # print(json.loads(headers))
    if protocol == "HTTP/1.1":
        if method == "GET":
            status_line, headers, payload = get(connection, route, headers, body)
        elif method == "POST":
            status_line, headers, payload = post(connection, route, headers, body)
        elif method == "PUT":
            status_line, headers, payload = put(connection, route, headers, body)
        elif method == "PATCH":
            status_line, headers, payload = patch(connection, route, headers, body)
            # if status_line["message"] == "No Content":
            #     http_response = "{protocol} {statcode} {message}\r\n{headers}\r\n".format(
            #         protocol=protocol,
            #         statcode=status_line["code"],
            #         message=status_line[
            #             "message"],
            #         headers=headers)
        elif method == "DELETE":
            status_line, headers, payload = delete(connection, route, headers)
        else:
            print("no sjit")

        http_response = "{protocol} {statcode} {message}\r\n{headers}\r\n\r\n{payload}".format(protocol=protocol,
                                                                                               statcode=status_line[
                                                                                                   "code"],
                                                                                               message=status_line[
                                                                                                   "message"],
                                                                                               headers=headers,
                                                                                               payload=payload)

        encoded = http_response.encode()
        print(db_driver.get_cursuri.cache_info())
        print(db_driver.get_favicon.cache_info())
        print("http_respo: ", encoded)
        endTime = time.time()
        duration = endTime - startTime
        with open("logging.txt", "a") as log:
            log.write('response: {response}\nendTime: {endTime}\nlatency: {latency}\n\n'
                      .format(response=http_response, endTime=endTime, latency=duration))
        connection.sendall(encoded)
    else:
        connection.sendall("protocol connection not supported".encode())

    connection.close()


def get(connection, route, headers, body=""):
    status = dict()
    payload = ''

    if "Mozilla/5.0" in headers["User-Agent"]:
        with open("index.html") as idx:
            payload = idx.read()
        status["code"] = config.status_codes["OK"]
        status["message"] = "OK"
        headers["content-length"] = len(payload)
        headers = helpers.construct_headers(headers)
        return status, headers, payload
    elif "Postman-Token" in headers.keys():
        if helpers.has_query_params(route):  # QUERY PARAM request
            route, params = helpers.split_route_with_query(route)
            params = helpers.split_params(params)

            if not params['id']:
                status["code"] = config.status_codes["Not Found"]
                status["message"] = "Not Found"
                payload = ""
                return status, headers, payload

            if route == "favicon.ico":
                status["code"] = config.status_codes["OK"]
                status["message"] = "OK"
                payload = db_driver.get_favicon()
            elif route == "studenti":
                headers["Content-Type"] = "application/json"
                returned = db_driver.get_studenti()
                if len(returned) == 0:
                    status["code"] = config.status_codes["Not Found"]
                    status["message"] = "Not Found"
                    payload = ""
                else:
                    status["code"] = config.status_codes["OK"]
                    status["message"] = "OK"
                    results = [dict(id=x[0], nume=x[1], nr_matricol=x[2]) for x in returned]
                    print(results)
                    payload = json.dumps(results)
            elif route == "cursuri":
                headers["Content-Type"] = "application/json"
                returned = db_driver.get_cursuri(int(params['id']))
                if len(returned) == 0:
                    status["code"] = config.status_codes["Not Found"]
                    status["message"] = "Not Found"
                    payload = ""
                else:
                    status["code"] = config.status_codes["OK"]
                    status["message"] = "OK"
                    results = [dict(id_curs=x[0], nume=x[1], credite=x[2]) for x in returned]
                    payload = json.dumps(results)
            elif route == "note":
                returned = db_driver.get_studenti(int(params['id']))
                if len(returned) == 0:
                    status["code"] = config.status_codes["Not Found"]
                    status["message"] = "Not Found"
                    payload = ""
                else:
                    status["code"] = config.status_codes["OK"]
                    status["message"] = "OK"
                    results = [dict(id_nota=x[0], nr_matricol=x[1], valoare=x[2], id_curs=x[3]) for x in returned]
                    payload = json.dumps(results)
            else:
                status["code"] = str(config.status_codes["Not Implemented"])
                status["message"] = "Not Implemented"
                payload = db_driver.get_501()

        else:
            route, resource_id = helpers.split_route_without_query(route)
            if resource_id == '':  # GET collection - WORKING - DON'T CHANGE
                if route == "favicon.ico":
                    status["code"] = config.status_codes["OK"]
                    status["message"] = "OK"
                    with open('favicon.ico', 'rb') as fav:
                        payload = fav.read()
                elif route == "studenti":
                    headers["Content-Type"] = "application/json"
                    returned = db_driver.get_studenti()
                    if len(returned) == 0:
                        status["code"] = config.status_codes["Not Found"]
                        status["message"] = "Not Found"
                        payload = ""
                    else:
                        status["code"] = config.status_codes["OK"]
                        status["message"] = "OK"
                        results = [dict(id=x[0], nume=x[1], nr_matricol=x[2]) for x in returned]
                        print(results)
                        payload = json.dumps(results)
                elif route == "cursuri":
                    print("colection")
                    returned = db_driver.get_cursuri()
                    if len(returned) == 0:
                        status["code"] = config.status_codes["Not Found"]
                        status["message"] = "Not Found"
                        payload = ""
                    else:
                        status["code"] = config.status_codes["OK"]
                        status["message"] = "OK"
                        results = [dict(id_curs=x[0], nume=x[1], credite=x[2]) for x in returned]
                        payload = json.dumps(results)
                elif route == "note":
                    returned = db_driver.get_studenti()
                    if len(returned) == 0:
                        status["code"] = config.status_codes["Not Found"]
                        status["message"] = "Not Found"
                        payload = ""
                    else:
                        status["code"] = config.status_codes["OK"]
                        status["message"] = "OK"
                        results = [dict(id_nota=x[0], nr_matricol=x[1], valoare=x[2], id_curs=x[3]) for x in returned]
                        payload = json.dumps(results)
                else:
                    status["code"] = str(config.status_codes["Not Implemented"])
                    status["message"] = "Not Implemented"
                    with open('501.html') as index:
                        payload = index.read()
            else:  # GET by resource_id - WORKING - DON'T CHANGE
                if route == "favicon.ico":
                    status["code"] = config.status_codes["OK"]
                    status["message"] = "OK"
                    with open('favicon.ico', 'rb') as fav:
                        payload = fav.read()
                elif route == "studenti":
                    headers["Content-Type"] = "application/json"
                    returned = db_driver.get_studenti(resource_id)
                    if len(returned) == 0:
                        status["code"] = config.status_codes["Not Found"]
                        status["message"] = "Not Found"
                        payload = ""
                    else:
                        status["code"] = config.status_codes["OK"]
                        status["message"] = "OK"
                        results = [dict(id=x[0], nume=x[1], nr_matricol=x[2]) for x in returned]
                        print(results)
                        payload = json.dumps(results)
                elif route == "cursuri":
                    returned = db_driver.get_cursuri(resource_id)
                    if len(returned) == 0:
                        status["code"] = config.status_codes["Not Found"]
                        status["message"] = "Not Found"
                        payload = ""
                    else:
                        status["code"] = config.status_codes["OK"]
                        status["message"] = "OK"
                        results = [dict(id_curs=x[0], nume=x[1], credite=x[2]) for x in returned]
                        payload = json.dumps(results)
                elif route == "note":
                    returned = db_driver.get_studenti(resource_id)
                    if len(returned) == 0:
                        status["code"] = config.status_codes["Not Found"]
                        status["message"] = "Not Found"
                        payload = ""
                    else:
                        status["code"] = config.status_codes["OK"]
                        status["message"] = "OK"
                        results = [dict(id_nota=x[0], nr_matricol=x[1], valoare=x[2], id_curs=x[3]) for x in returned]
                        payload = json.dumps(results)
                else:
                    status["code"] = str(config.status_codes["Not Implemented"])
                    status["message"] = "Not Implemented"
                    with open('501.html') as index:
                        payload = index.read()
    # headers["Content-Type"] = ?
    headers["content-length"] = len(payload)
    headers = helpers.construct_headers(headers)
    return status, headers, payload


def post(connection, route, headers, body):
    status = dict()
    payload = ""
    if "Mozilla/5.0" in headers["User-Agent"]:
        print(route, headers, body)
        arglist = json.loads(body)
        route, params = helpers.split_route_without_query(route)
        insertion_status = db_driver.insert_into_cursuri(arglist)
        print("STATUS:", insertion_status, type(insertion_status))
        if isinstance(insertion_status, int):
            print("SADASDSADAS")
            # status["code"] = config.status_codes["Created"]
            # status["message"] = "Created"
            # headers["Location"] = '/cursuri/{id}'.format(id=insertion_status)
            # headers["Content-Type"] = "application/json"
            # # payload = json.loads(str(insertion_status))
        else:
            print("not created", insertion_status)
            status["code"] = config.status_codes["Conflict"]
            status["message"] = "Conflict"
            # ???? may cause ERRORS >
            payload = "insertion_status"
        # with open("index.html") as idx:
        #     payload = idx.read()
        # status["code"] = config.status_codes["OK"]
        # status["message"] = "OK"
        headers["content-length"] = len(payload)
        headers = helpers.construct_headers(headers)
        return status, headers, payload

    if helpers.has_query_params(route):
        status["code"] = config.status_codes["Forbidden"]
        status["message"] = "Forbidden"
        payload = ""
    else:
        body = helpers.split_params(body)
        route, params = helpers.split_route_without_query(route)
        print(body, route, params)
        if route == "cursuri":
            insertion_status = db_driver.insert_into_cursuri(body)
            if isinstance(insertion_status, int):
                print("Created")
                status["code"] = config.status_codes["Created"]
                status["message"] = "Created"
                headers["Location"] = '/cursuri/{id}'.format(id=insertion_status)
                headers["Content-Type"] = "application/json"
                # payload = json.loads(str(insertion_status))
            else:
                # print("not created", insertion_status)
                status["code"] = config.status_codes["Conflict"]
                status["message"] = "Conflict"
                # print(insertion_status)
                # ???? may cause ERRORS >
                payload = json.dumps(insertion_status)
                # print(payload)
        else:
            status["code"] = config.status_codes["Not Implemented"]
            status["message"] = "Not Implemented"
            payload = ""
    headers["content-length"] = len(payload)
    headers = helpers.construct_headers(headers)
    return status, headers, payload


def put(connection, route, headers, body=""):
    status = dict()
    payload = ""
    print("putting")
    if helpers.has_query_params(route):
        status["code"] = config.status_codes["Forbidden"]
        status["message"] = "Forbidden"
        payload = ""
    else:
        body = helpers.split_params(body)
        route, resource_id = helpers.split_route_without_query(route)

        if route == "cursuri":
            if "id_curs" in body.keys():
                print(type(resource_id), type(body["id_curs"]))
                if resource_id is not body["id_curs"]:
                    status["code"] = config.status_codes["Conflict"]
                    status["message"] = "Conflict"
                    payload = "Resource id is not the same with the one provided in request body"
            put_status = db_driver.put_cursuri(resource_id, body)
            if isinstance(put_status, int):  # success
                if put_status == 0:
                    status["code"] = config.status_codes["Not Found"]
                    status["message"] = "Not Found"
                    payload=""
                else:
                    status["code"] = config.status_codes["No Content"]
                    status["message"] = "No Content"
                    payload = ""
            else:  # bad parameters
                status["code"] = config.status_codes["Not Acceptable"]
                status["message"] = "Not Acceptable"
                payload = put_status
        else:
            status["code"] = config.status_codes["Not Implemented"]
            status["message"] = "Not Implemented"
            payload = ""
    headers["content-length"] = len(payload)
    headers = helpers.construct_headers(headers)
    return status, headers, payload


def patch(connection, route, headers, body=''):
    # IF-MATCH / ETAG header ???
    status = dict()
    payload = ""
    if helpers.has_query_params(route):
        status["code"] = config.status_codes["Forbidden"]
        status["message"] = "Forbidden"
        payload = ""
    else:
        body = helpers.split_params(body)
        route, resource_id = helpers.split_route_without_query(route)
        print(route, headers, resource_id, body)

        if route == "cursuri":
            ret_id = db_driver.patch_cursuri(resource_id, body)
            print("res id", resource_id)
            print("ret id", ret_id)
            if isinstance(ret_id, int):
                if ret_id == 0:  # failed update
                    status["code"] = config.status_codes["Not Found"]
                    status["message"] = "Not Found"
                    payload = ""

                elif ret_id == 1:  # succes update
                    status["code"] = config.status_codes["No Content"]
                    status["message"] = "No Content"
                    payload = ""
            else:  # bad parameters
                status["code"] = config.status_codes["Not Acceptable"]
                status["message"] = "Not Acceptable"
                payload = ""
        else:
            status["code"] = config.status_codes["Not Implemented"]
            status["message"] = "Not Implemented"
            payload = ""
    headers["content-length"] = len(payload)
    headers = helpers.construct_headers(headers)
    return status, headers, payload


def delete(connection, route, headers, body=''):
    status = dict()
    payload = ""
    if helpers.has_query_params(route):
        status["code"] = config.status_codes["Forbidden"]
        status["message"] = "Forbidden"
        payload = ""
    else:
        route, resource_id = helpers.split_route_without_query(route)

        if route == "cursuri":
            if resource_id == "":
                status["code"] = config.status_codes["Method Not Allowed"]
                status["message"] = "Method Not Allowed"
                payload = "I can't let you do this. Try one by one"
            else:
                ret_id = db_driver.delete_cursuri(resource_id)
                print("ret ", ret_id)
                if isinstance(ret_id, int):
                    if ret_id == 1:
                        status["code"] = config.status_codes["OK"]
                        status["message"] = "OK"
                        payload = ""
                    else:
                        status["code"] = config.status_codes["Not Found"]
                        status["message"] = "Not Found"
                        payload = ""
                else:
                    status["code"] = config.status_codes["Not Modified"]
                    status["message"] = "Not Modified"
                    payload = ""
        else:
            status["code"] = config.status_codes["Not Implemented"]
            status["message"] = "Not Implemented"
            payload = ""
    headers["content-length"] = len(payload)
    headers = helpers.construct_headers(headers)
    return status, headers, payload
