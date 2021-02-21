from flask import Blueprint

api = Blueprint('auto_evaluate_v3', __name__, url_prefix='/v3')

from .auto_evaluate import *
