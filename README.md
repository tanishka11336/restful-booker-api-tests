# Restful-Booker API Test Automation (Python PyTest + REST Assured)

API test automation for [Restful-Booker](https://restful-booker.herokuapp.com), a public practice REST API.
The main suite uses **Python, requests and PyTest**. A smaller **Java REST Assured + TestNG** module is included.

## Features

- Reusable API client (`utils/api_client.py`) wrapping every endpoint, so tests stay short
- Full CRUD coverage: create, read, update (PUT), partial update (PATCH), delete
- Authentication: token generation, and tests for missing/invalid tokens
- **JSON schema validation** of responses (`jsonschema`)
- **Data-driven tests** from `test_data/bookings.json`
- Fixtures that create test data and always clean it up (`created_booking`)
- Negative tests: invalid credentials, 403 without token, 404 for unknown id, malformed payloads
- Query-parameter filtering, response-time check
- Logging of every request to `logs/api_tests.log`
- HTML report, `smoke` / `regression` / `negative` markers, parallel run support
- GitHub Actions workflow running both the Python and Java suites

## Project structure

```
restful-booker-api-tests/
├── conftest.py              # client, token and test-data fixtures, CLI options
├── pytest.ini
├── requirements.txt
├── tests/
│   ├── test_auth.py
│   ├── test_booking_crud.py
│   └── test_booking_validation.py
├── utils/
│   ├── api_client.py
│   ├── schemas.py
│   ├── data_reader.py
│   └── logger.py
├── test_data/bookings.json
├── java-restassured/        # REST Assured + TestNG module (Maven)
│   ├── pom.xml
│   ├── testng.xml
│   └── src/test/java/com/example/api/BookingApiTest.java
└── .github/workflows/ci.yml
```

## Run the Python tests

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

pytest                            # everything
pytest -m smoke                   # quick checks
pytest -m negative                # negative tests only
pytest -n 2                       # parallel
```

Report: `reports/report.html`

## Run the Java REST Assured tests

Requires JDK 17+ and Maven.

```bash
cd java-restassured
mvn test
```

## Endpoints covered

| Method | Endpoint | Checked |
|--------|----------|---------|
| POST | `/auth` | token returned, bad credentials rejected |
| GET | `/ping` | health check |
| GET | `/booking` | id list, schema, name filters |
| GET | `/booking/{id}` | body, schema, 404 for unknown id |
| POST | `/booking` | data-driven creation, malformed payloads |
| PUT | `/booking/{id}` | full update, 403 without/with bad token |
| PATCH | `/booking/{id}` | partial update leaves other fields untouched |
| DELETE | `/booking/{id}` | 201 response, 404 afterwards, 403 without token |

## Notes

- This is a shared public sandbox: data is reset periodically and the server can be slow on first call (cold start). Re-run if the first request times out.
- Restful-Booker has quirks (e.g. `/ping` and `DELETE` return 201, bad credentials return 200 with a `reason`). The tests assert the API's real behaviour and say so in comments.
