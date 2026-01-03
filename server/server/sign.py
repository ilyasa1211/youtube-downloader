import hmac
import hashlib
from .common.types import SignatureVerifier, SignatureGenerator


class HMACSigner(SignatureGenerator, SignatureVerifier):
    __secret: str

    def __init__(self, secret: str) -> None:
        super().__init__()
        self.__secret = secret

    def Generate(self, content: str) -> str:
        b = hmac.new(
            self.__secret.encode("utf-8"), content.encode("utf-8"), hashlib.sha256
        ).digest()

        return b.decode("utf-8")

    def Verify(self, content: str, signature: str) -> bool:
        expected = self.Generate(content)

        return hmac.compare_digest(expected, signature)
