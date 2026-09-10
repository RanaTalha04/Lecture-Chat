"""Application exception helpers."""

import sys


def error_message_detail(error: Exception, error_detail: object) -> str:
    _, _, exc_tb = error_detail.exc_info()
    if exc_tb is None:
        return str(error)
    filename = exc_tb.tb_frame.f_code.co_filename
    return f"Error in [{filename}] at line [{exc_tb.tb_lineno}]: {error}"


class CustomException(Exception):
    def __init__(self, error_message: Exception, error_detail: object = sys):
        self.error_message = error_message_detail(error_message, error_detail)
        super().__init__(self.error_message)
