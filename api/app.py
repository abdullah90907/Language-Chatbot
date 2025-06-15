from flask import Flask
from api.index import app

def handler(request):
    return app
