class BaseRepoError(Exception):
    model_name: str
    problem: str = "Unknown problem"
    detail: dict

    def __init__(self, model_name: str, detail: dict):
        super().__init__()
        self.model_name = model_name
        self.detail = detail
