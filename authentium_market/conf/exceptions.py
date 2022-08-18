class APIException(Exception):
    code = 400
    title = 'Invalid request'
    detail = 'Invalid request'

    def __init__(self, detail=None, params=None):

        if params:
            errors = []
            for key in params:
                if isinstance(params[key], dict):
                    errors.append(f"{key}: Invalid Parameter")
                else:
                    errors.append(f"{key}: {','.join(params[key])}")
            self.detail = '|'.join(errors)
        elif detail is not None:
            self.detail = str(detail)
