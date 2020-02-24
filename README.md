# Marvel Code Test

![Running-Solution](https://raw.githubusercontent.com/faiyaz7283/gifs/master/mct.gif)

### Running the project

- Clone the repo
- Navigate to the root of the project
- Run the command: `cp .env.example .env`
- The above command will create a new .env file
- You may change the default values, or leave them as is
- The two important keys are PUBLIC_KEY and PRIVATE_KEY. You MUST add your Marvel API-keys into them
- Save and close the file
- Next, we will kick off the build script to initialize and start the project
- The whole process from start to finish may take anywhere from 20 to 30 minutes. You have been WARNED!
- Open up a terminal window and run `./bin/build.sh start`
- The above command will trigger the build script and kick-off `docker-compose`
- Docker will pull new/update images required for the project
- DB: MariaDB image container will load a new empty database with the value provided with MYSQL_DATABASE
- Cache: Redis will initialize and start listening on port 6379
- Loader: Python worker, calls the marvels public API to fetch all the 'characters' and 'creators' along with all their associated series_id's. It batches up all the records and loads them to the database. It also normalizes the relation between character and creators by connecting the two entities with many to many relations.
- API:  A Flask application, runs a basic python webserver on port 8080. The two available endpoints are:
    - "/api/v1/characters/<int:id>/creators" - get all character creators with the character id
    - "/api/v1/creators" - get all available creators
    - "/api/v1/creators?character_name=<name>" - get all creators for the character name
- Although not a separate service, the build script will finish with running all the integration tests

The build.sh script provided is just for convenience. You can run all these commands manually if you needed to intervene 
- Running `docker-compose up` will bring up all the services in the foreground. Add a `-d` flag if you rather have it in background
- Next, log into the "loader" container and run the loader.py script - `docker-compose exec loader bash` and `python -m loader`. This will load up the database with data fetched from Marvel API. You may exit the container.
- Once the loading is complete, feel free to run the integration tests to make sure the project API is working correctly. To kick off the tests, log into the "api" container - `docker-compose exec api bash` and `cd /src && python -m pytest -vv`. Set groups of tests will run on the two available API endpoints. All tests should pass. You may exit the container.
- Now you are free to open a browser, or a rest client application and visit "localhost:8080/api/v1/characters/<int:id>/creators" and "/api/v1/creators?character_name=<name>" to test out the API.
- Be aware; there is a rate limiter setup - which is set to "100/hour" and "1000/day". You can check your hourly rate limit from the response headers.

## The database model

![DB-Model-edr](https://raw.githubusercontent.com/faiyaz7283/gifs/master/edr.jpg)
