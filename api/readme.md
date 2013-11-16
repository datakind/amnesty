Amnesty API
===========

This is a simple postgres store and `flask` API for the amnest int'l datakind project.

## Setup
Create a `postgres` database and export the path as an Environmental Variable
```
export DATABASE_URL='postgresql://brian:mc@localhost:5432/amnesty'
```

## Requirements
```
pip install -r requirements.text
```

## Build database
```
python build_db.py
```

## Host API
```
python api.py
```