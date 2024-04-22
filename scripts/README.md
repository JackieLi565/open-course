# Web Scripts

Python program to collect public course data from [TMU](https://www.torontomu.ca/)

## Getting Started

First you will need to setup the database configuration. Create a `database.config.json` within the `scripts` directory and fill in your database credentials.

```json
{
  "host": "database host",
  "database": "database name",
  "user": "postgresql user",
  "password": "user password"
}
```

You can then install the dependency using [Poetry](https://python-poetry.org/)

```bash
poetry install
```
