from werkzeug.exceptions import HTTPException
from flask import make_response

class NotFoundError(HTTPException):
    def __init__(self, status_code):
        self.response = make_response('', status_code)
    
class BusinessValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        msg = {"status_code": status_code, "error_code": error_code, "error_message": error_message}
        self.response = make_response(msg, status_code)

class SimilarUserExists(HTTPException):
    def __init__(self, error_code, error_message):
        msg = {"error_code": error_code, "msg": error_message}
        self.response = make_response(msg, error_code)