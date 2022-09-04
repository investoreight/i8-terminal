from i8_terminal.api.service_result import ServiceResult


class FinancialsListResult(ServiceResult):
    
    def __init__(self, data, context=None):
        super().__init__(data, context)

    
