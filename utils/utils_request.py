from django.http import JsonResponse


def request_failed(code, info, status_code=400):
    return JsonResponse({
        "code": code,
        "info": info,
        },
        headers={
            "Access-Control-Allow-Origin": "*"
        },
      status=status_code)


def request_success(data={},info="Succeed", status_code=200):
    return JsonResponse({
        "code": 0,
        "info": info,
        **data
    },
    headers={
        "Access-Control-Allow-Origin": "*"
    },
    status=status_code)


def return_field(obj_dict, field_list):
    for field in field_list:
        assert field in obj_dict, f"Field `{field}` not found in object."

    return {
        k: v for k, v in obj_dict.items()
        if k in field_list
    }

CREATE_SUCCESS = request_success(info="Created successfully", status_code=201)
UPDATE_SUCCESS = request_success(info="Updated successfully", status_code=200)
DELETE_SUCCESS = request_success(info="Deleted successfully", status_code=200)

BAD_METHOD = request_failed(-3, "Bad method", 405)
BAD_PARAMS = request_failed(-4, "Bad parameters", 400)
USER_NOT_FOUND = request_failed(-5, "User not found", 404)
FRIENDSHIP_NOT_FOUND = request_failed(-6, "Friendship not found", 404)
ALREADY_EXIST = request_failed(-7, "Already exist", 403)
