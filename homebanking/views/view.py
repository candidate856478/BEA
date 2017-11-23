from pyramid.response import Response
from pyramid.view import view_config
 
from ..security import is_valid_user
from pyramid.security import (
    remember,
    )
 
from sqlalchemy.exc import DBAPIError
 
from ..models import (
    DBSession,
    )
 
from pyramid.httpexceptions import (
    HTTPFound,
    )
 
 
@view_config(route_name='login', renderer='../templates/login.pt')
def login_view(request):
    url = request.route_url('login')
    login = ''
    message = ''
 
    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']
        if is_valid_user(login,password):
            headers = remember(request, login)
            return HTTPFound(location = request.route_url('item_action', action='view'),
                             headers = headers)
 
        message = 'Wrong username/password'
 
 
    return dict(url=url, login=login, message=message)