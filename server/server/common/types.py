from typing import Any, Protocol


class Error:
    __code: int
    __message: str

    def __init__(self, code: int, message: str) -> None:
        self.__code = code
        self.__message = message

    def get_message(self) -> str:
        return self.__message

    def get_code(self) -> int:
        return self.__code


class Result:
    __result: Any | None
    __error: Error | None

    def __init__(self, result: Any | None, error: Error | None = None) -> None:
        self.__result = result
        self.__error = error
        pass

    def ok(self) -> bool:
        return self.__result is not None

    def error(self) -> bool:
        return self.__error is not None

    def __iter__(self):
        yield self.__result
        yield self.__error


class SignatureGenerator(Protocol):
    def Generate(self, content: str) -> bytes: ...


class SignatureVerifier(Protocol):
    def Verify(self, content: str, signature: bytes) -> bool: ...
