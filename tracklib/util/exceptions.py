# For type annotation
from __future__ import annotations   
from typing import Any, Optional, Union


# =============================================================================
#   List of custom exceptions for Tracklib
# =============================================================================
class AnalyticalFeatureError(Exception):
    pass
class OperatorError(Exception):
    pass
class QueryError(Exception):
    pass
class KernelError(Exception):
    pass
class CoordTypeError(Exception):
    pass
class NotYetImplementedError(Exception):
    pass
class UnknownModeError(Exception):
    pass
class MathError(Exception):
    pass
class SizeError(Exception):
    pass
class MissingArgumentError(Exception):
    pass
class IOPathError(Exception):
    pass
class WrongArgumentError(Exception):
    pass
class NetworkError(Exception):
    pass