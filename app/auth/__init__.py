from flask import Blueprint
from ..models import Permission
auth = Blueprint('auth',__name__)

from . import views
