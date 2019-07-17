# gwas-sumstats-service
## GWAS summary statistics service app

This handles the uploaded summary statistics files, validates them, reports errors to the deposition app and puts valid files in the queue for sumstats file harmonisation and HDF5 loading.

## Installation

- Clone the repository
  - `git clone https://github.com/EBISPOT/gwas-sumstats-service.git`
  - `cd gwas-sumstats-service`
- Set up environment
  - `virtualenv --python=python3.6 .env`
  - `source activate .env`
- Install
  - `pip install .`
  
## Run the tests

- `./run_tests.sh`

## Run the app

- Start the flask app on http://localhost:5000
  - `export FLASK_APP=sumstats_service.app`
  - `flask run`

### Example POST method
```
curl -i -H "Content-Type: application/json" -X POST -d '{"requestEntries":[{"id":"abca1234a","pmid":"1233454","filePath":"file/path.tsv","md5":"b1d7e0a58d36502d59d036a17336ddf5","assembly":"38"},{"id":"abca1234","pmid":"1233454","filePath":"file/path.tsv","md5":"b1d7e0a58d36502d59d036a17336ddf5","assembly":"38"}]}' http://localhost:5000/sum-stats

HTTP/1.0 201 CREATED
Content-Type: application/json
Content-Length: 26
Server: Werkzeug/0.15.4 Python/3.6.5
Date: Wed, 17 Jul 2019 15:15:23 GMT

{"callbackID": "TiQS2yxV"}
```

### Example GET method (using callback id from above)
```
curl http://localhost:5000/sum-stats/TiQS2yxV

{
  "callbackID": "TiQS2yxV",
  "completed": false,
  "statusList": [
    {
      "id": "abca12",
      "status": "VALIDATING",
      "error": null
    },
    {
      "id": "ca1234",
      "status": "VALIDATING",
      "error": null
    }
  ]
}
```

