from fastapi import HTTPException


class ApiNotFound(HTTPException):
    status_code = 404

    def __init__(self, model_name: str, detail: dict = None):
        self.model_name = model_name
        self.detail = detail

    def __str__(self):
        return f"{self.model_name} not found. {self.detail}"
