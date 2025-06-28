from flask import Blueprint

main = Blueprint('main', __name__)
from flask import Blueprint

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return "AOC Inventory App is running!"