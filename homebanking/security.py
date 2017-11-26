import transaction
from hashlib import sha256
from sqlalchemy.exc import DBAPIError
from pyramid.security import authenticated_userid

from .models import (
    Client
    )
 
def is_valid_user(username, password, request):
    """Check if the given user/password is a valid
    user for the system.
    """
    salted_password = username + ":" + password
    pwd = sha256(salted_password.encode("utf-8")).hexdigest()
    
    try:
        return request.dbsession.query(Client.id).\
                    filter(Client.login == username, Client.password == pwd).scalar()
    except DBAPIError:
        return Response("Error executing login request", content_type='text/plain', status=500)
 
def groupfinder(username, request):
    """Authentication policy callback.
 
    *    If the userid exists in the system, it will return a sequence of group identifiers (or an empty sequence if the user isn't a member of any groups).
    *    If the userid does not exist in the system, it will return None.
    
    All users will have the same group membership, just cheking for user existence
 
    """
    try:
        existing_user = request.dbsession.query(Client.id).\
                    filter(Client.login == username).scalar()
    except DBAPIError:
        return Response("Error executing group finder request", content_type='text/plain', status=500)
    
    return ['editor'] if existing_user else None

def resourceAccessAllowed(userId, request):
    """ Verify if user logged in is working on his client data.
    """
    allowed = False
    
    try:
        login = authenticated_userid(request)
        same_user = request.dbsession.query(Client.id).\
                    filter(Client.login == login, Client.id == userId).scalar()
        
        if same_user:
            allowed = True
    except DBAPIError:
        return Response("Error executing access check request", content_type='text/plain', status=500)
    
    return allowed
    