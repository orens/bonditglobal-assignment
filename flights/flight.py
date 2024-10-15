from dataclasses import dataclass
from datetime import datetime, time, timedelta
from enum import Enum, auto
from typing import Any, ClassVar, Optional

from flights.errors import CsvMalformedError


class SuccessStatus(Enum):
    MISSING = auto()
    SUCCESS = auto()
    FAIL = auto()


@dataclass
class Flight:
    CSV_COLUMNS: ClassVar[list[str]] = (
        [  # Column names are copied as-is from the sample CSV
            "flight ID",
            "Arrival",
            "Departure",
            "success",
        ]
    )

    _TIME_FORMAT: ClassVar[str] = "%H:%M"
    _BASE_DATETIME = datetime(
        1, 1, 1, 0, 0
    )  # used to calculate ground time. value is not important

    flight_id: str
    arrival: time
    departure: time
    success: SuccessStatus = SuccessStatus.MISSING

    def __str__(self):
        return (
            f"{self.flight_id}: {self.arrival.time()}-{self.departure.time()} "
            + f"(ground time: {self.ground_time}): {self.success.name.lower()}"
        )

    @property
    def ground_time(self) -> timedelta:
        return datetime.combine(self._BASE_DATETIME, self.departure) - datetime.combine(
            self._BASE_DATETIME, self.arrival
        )

    @classmethod
    def from_csv_row(self, row: list) -> Optional["Flight"]:
        row = [field.strip() for field in row]  # making input canonized
        if not row:
            # Ignoring empty lines
            return None
        if len(row) < len(self.CSV_COLUMNS) - 1:
            # ignoring 'success' column, since it should be decided by the Airport
            raise CsvMalformedError(f"Row missing required information: {row}")
        return Flight(
            flight_id=row[0],
            arrival=time.fromisoformat(row[1]),
            departure=time.fromisoformat(row[2]),
        )

    def as_csv_row(self) -> tuple:
        return (
            self.flight_id,
            self.arrival.strftime(self._TIME_FORMAT),
            self.departure.strftime(self._TIME_FORMAT),
            self.success.name.lower(),
        )
