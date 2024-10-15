from asyncio import Lock
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import time
from os import getenv
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from flights.airport import Airport
from flights.errors import FlightsInvalidDataError, NoSuchFlightError
from flights.flight import Flight

_DEFAULT_DATABASE_NAME = "./flights_database.csv"


@dataclass
class _ServerState:
    database: Path
    airport: Airport = Airport()
    lock: Lock = Lock()


_state: _ServerState = None


class FlightModel(BaseModel):
    flight_id: str
    arrival: time
    departure: time

    def as_flight(self) -> Flight:
        return Flight(
            flight_id=self.flight_id,
            arrival=self.arrival.replace(tzinfo=None),
            departure=self.departure.replace(tzinfo=None),
        )


class FlightViewModel(FlightModel):
    success: str

    @classmethod
    def from_flight(cls, flight: Flight) -> "FlightViewModel":
        return FlightViewModel(
            flight_id=flight.flight_id,
            arrival=flight.arrival,
            departure=flight.departure,
            success=flight.success.name.lower(),
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _state
    _state = _ServerState(
        Path(getenv("FLIGHTS_DATABASE_CSV_FILE", _DEFAULT_DATABASE_NAME))
    )
    async with _state.lock:
        if _state.database.exists():
            _state.airport.load_csv(_state.database)
        # Making sure DB and flights are in order (even on initial DB):
        _state.airport.dump_processed_csv(_state.database)
    yield
    async with _state.lock:
        _state.airport.dump_processed_csv(_state.database)


app = FastAPI(lifespan=lifespan)


@app.get("/flights/{flight_id}")
async def get_flight(flight_id: str) -> FlightViewModel:
    async with _state.lock:
        try:
            return FlightViewModel.from_flight(_state.airport.get_flight(flight_id))
        except NoSuchFlightError as reason:
            raise HTTPException(
                status_code=404, detail=f"Error in input: {reason}"
            ) from reason
        except FlightsInvalidDataError as reason:
            raise HTTPException(
                status_code=400, detail=f"Error in input: {reason}"
            ) from reason
        except HTTPException as reason:
            raise HTTPException(status_code=500, detail="Unknown Error") from reason


@app.post("/flights")
async def create_flight(flight_model: FlightModel) -> FlightViewModel:
    async with _state.lock:
        try:
            _state.airport.add_flight(flight_model.as_flight())
            _state.airport.dump_processed_csv(_state.database)  # Keep changes
            return FlightViewModel.from_flight(
                _state.airport.get_flight(flight_model.flight_id)
            )
        except FlightsInvalidDataError as reason:
            raise HTTPException(
                status_code=400, detail=f"Error in input: {reason}"
            ) from reason
        except HTTPException as reason:
            raise HTTPException(status_code=500, detail="Unknown Error") from reason
