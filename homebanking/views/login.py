from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import (
    remember,
    forget,
    )
from ..security import is_valid_user

@view_config(route_name='login', renderer='../templates/login.pt')
def login_view(request):
    url = request.route_url('login')
    url_register = request.route_url('client_action', action='add', id='NEW')
    login = ''
    message = ''
 
    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']
        clientId = is_valid_user(login,password,request)
        if clientId:
            headers = remember(request, login)
            return HTTPFound(
                location = request.route_url('client_action', action='view', id=clientId),
                headers = headers,
                )
 
        message = 'Wrong username/password'
 
 
    return dict(url=url, login=login, message=message, url_register=url_register)

@view_config(route_name='logout', renderer='../templates/login.pt')
def logout_view(request):
    headers = forget(request)
    url = request.route_url('login')
    return HTTPFound(location=url, headers=headers)