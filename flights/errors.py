class FlightsException(Exception):
    pass


class FlightsInvalidDataError(FlightsException):
    """denotes an error in input"""

    pass


class DuplicateFlightError(FlightsInvalidDataError):
    pass


class NoSuchFlightError(FlightsInvalidDataError):
    pass


class CsvMalformedError(FlightsInvalidDataError):
    pass
