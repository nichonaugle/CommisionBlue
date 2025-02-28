from enum import Enum

class CurveType(Enum):
    """
    CurveType is an enumeration that defines types of cryptographic curves. Must be the same for both client and server!

    Attributes:
        CURVE25519 (str): Represents the Curve25519 elliptic curve.
        CURVE448 (str): Represents the Curve448 elliptic curve.
    """
    CURVE25519 = "curve25519"
    CURVE448 = "curve448"