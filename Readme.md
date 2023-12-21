# AAT Backend

## Create virtual env

```bash
$ python -m venv env
$ ./env/scripts/activate
```

## Install requirements

```bash
$ pip install -r requirements.txt
```

## Run the backend

```bash
$ uvicorn aat_backend.main:app --host 0.0.0.0 --reload
```
