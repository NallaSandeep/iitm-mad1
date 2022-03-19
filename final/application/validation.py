from flask import make_response
from werkzeug.exceptions import HTTPException
import json


class BusinessValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        error_json = {"error_code": error_code, 'error_message': error_message}
        self.response = make_response(json.dumps(error_json), status_code)


class InputValidationError(HTTPException):
    def __init__(self, status_code, error_message):
        self.response = make_response(error_message, status_code)