# laughing-octo-pancake

Initial command to build, create docker network and run migrations
```
make install
```

Start project (monitoring service is included in docker compose so no need to start manually in terminal)
```
make start
```

Feel free to check Makefile for further commands


A few things to consider. Initially there is no Plant in the database.
You will have to create Plants either from admin... or through api calls.
Periodic task is configured to run everyday at 1am. You can change it
to every few minutes to pull data from monitoring service sooner.