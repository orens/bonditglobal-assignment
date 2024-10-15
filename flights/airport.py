from csv import reader, writer
from datetime import timedelta
from pathlib import Path

from flights.errors import DuplicateFlightError, NoSuchFlightError
from .flight import Flight, SuccessStatus


class Airport:
    class Defaults:
        MAX_FLIGHTS_PER_DAY: int = 20
        MIN_GROUND_TIME: timedelta = timedelta(hours=3)

    def __init__(
        self,
        max_flights_per_day: int = Defaults.MAX_FLIGHTS_PER_DAY,
        min_ground_time_minutes: timedelta = Defaults.MIN_GROUND_TIME,
    ):

        self._flights: dict[str, Flight] = {}
        self._max_flights_per_day: int = max_flights_per_day
        self._min_ground_time_minutes: int = min_ground_time_minutes
        self._success_count: int = 0

    def reset(self) -> None:
        self._flights = {}
        self._success_count = 0

    def get_flight(self, flight_id: str) -> Flight:
        try:
            return self._flights[flight_id]
        except KeyError:
            raise NoSuchFlightError(f'Flight does not exist: {flight_id}')

    def add_flight(self, flight: Flight) -> None:
        if flight.flight_id in self._flights:
            raise DuplicateFlightError(f"Duplicate flight ID: {flight.flight_id}")
        if (
            self._success_count > self._max_flights_per_day
            or flight.ground_time < self._min_ground_time_minutes
        ):
            flight.success = SuccessStatus.FAIL
        else:
            flight.success = SuccessStatus.SUCCESS
            self._success_count += 1
        self._flights[flight.flight_id] = flight

    def dump_processed_csv(self, csv_path: Path):
        with open(csv_path, "w") as input_file:
            csv_writer = writer(input_file)
            csv_writer.writerow(Flight.CSV_COLUMNS)
            for flight in sorted(
                self._flights.values(), key=lambda flight: flight.arrival
            ):
                csv_writer.writerow(flight.as_csv_row())

    def load_csv(self, csv_path: Path) -> None:
        with open(csv_path) as input_file:
            csv_reader = reader(input_file)
            next(csv_reader)  # ignore title row
            for row in csv_reader:
                flight = Flight.from_csv_row(row)
                if flight is None:
                    continue  # Empty line
                self.add_flight(flight)

    def __str__(self):
        return f'Airport:\n{''.join((f"- {flight}\n" for flight in self._flights))}'
