# CRM
This project is a very minimal version of the CRM system.
Currently the project hasn't deployed in the AWS, I have created a minimal terraform code to deploy it there

## Instructions to set-up the environment
```
python -m venv venv
venv\Scripts\activate
cd backend
pip install -r requirements.txt
```

## Instructions to run the application in local
```
uvicorn app.main:app --reload --port 8000
```
