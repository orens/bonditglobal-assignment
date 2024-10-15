### Assignment Solution - External Documentation
This is the solution to the "Flights" assignment. It implements a CLI utility and a web server, both using the same "Airport" implementation.

## Installation
The file `pyproject.toml` uses `poetry` and contains all the requirements for running the project. The lockfile describes the specific versions locked in my development.
Running `poetry init` should set you up with a virtual environment, and, after `poetry install`, prefixing the commands with `poetry run` will use the created virtualenv.

For the sake of bravity, `poetry run` is implied in commands throughout this document.

## Running
The commands here are also part of `.vscode/launch.json` and all the required arguments are also provided there.

## Add a `success` column to an existing csv file:
```
 $ python -m cli update-dataset input.csv output.csv
```
or
```
 $ python -m cli update-dataset -f input-output.csv
```
for in place update (note the `-f` flag to allow such rewrite)

## See CLI flags
```
 $ python -m cli --help
```

### Run the web server
```
 $ python -m fastapi dev ./server/server.py    
```
or, for release mode:
```
 $ python -m fastapi run ./server/server.py    
```

## Design considerations
### Database
Since a CSV implementation is required in the assignment, and due to time limitations, I decided to use at as a base layer for the database of the server.
This had some major drawbacks. Namely, locking of the database (see "locking") below and performance.

### Database writes
Since I wanted persistency even in case of a fault, I wrote the entire file on every POST. If I had more time for it, I would have elected to go with a database, probably SQL, and probably running on an accompanying container described as a DockerFile.

### Locking
Since the database is rewritten on every POST, locking should be employed as a protection. Again, have I had more time, I would probably use a background thread consuming updates from a queue (synchronized) and batching update (for eventual consistency) or, of course, a real SQL database.

### Testing
I did some testing, as time permitted, manually. I didn't implement unit/automated tests.

### Other
- The web server's database filename is `flights_database.csv` by default and can be changed by setting the environment variable `FLIGHTS_DATABASE_CSV_FILE`
- FastAPI's server also include a documentation endpoint under `/docs` which is very nice to work with and documents the API
- Schema validation is also done automatically
- Since the assignment doesn't describe time folding (for instance, landing at 23:00 and taking off again at 3:00) and the input format doesn't support them, I ignored them as well.
- The file `sample.csv` contains the sample from the pdf. The file `input.csv` contains the same input, with duplicate rows filtered.
- *IDs are case sensitive* - insensitivity is easy to implement but seem to require an explicit requirement.
- Timestamps in JSON are different than the CSV. This is JSON, by convention, recommends it.
- The returned body from a POST request, if successful, is the same as a GET for the same flight, to allow for an update of flight status to the client
