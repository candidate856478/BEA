import transaction
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.security import forget
from pyramid.httpexceptions import HTTPFound
from sqlalchemy.exc import DBAPIError
from hashlib import sha256
from urllib.request import urlopen
import xml.etree.ElementTree as ET
from ..security import resourceAccessAllowed
from ..models import (
    Client,
    Account,
    AccountType,
    AccountClient,
    clientValidation,
    )
from ..common import deleteAccount

@view_config(
    route_name='client_action', 
    match_param='action=view',
    renderer='../templates/client_view.pt',
    permission='edit',
    )
def client_view(request):
    """ Display client details
    """
    clientId = request.matchdict["id"]
    if not resourceAccessAllowed(clientId, request):
        return Response("Error: Access not allowed on this resource.", content_type='text/plain', status=403)
    logout_url = request.route_url('logout')
    update_url = request.route_url('client_action', action='update', id=clientId)
    delete_url = request.route_url('client_action', action='delete', id=clientId)
    accounts_url = request.route_url('account_list', clientId=clientId)
    
    try:
        client = request.dbsession.query(Client).filter(Client.id == clientId).first()
        
        #Store data to pre fill update form
        request.session['client_login'] = client.login
        request.session['client_name'] = client.name
        request.session['client_first_name'] = client.first_name
        request.session['client_birth_date'] = client.birth_date
        request.session['client_address'] = client.address
        
        if client.lat == 0.0 and client.lng == 0.0:
            coordinates = 'Not specified.'
        else:
            coordinates = str(client.lat) + ' ; ' + str(client.lng)
    except DBAPIError:
        return Response("Error retrieving current client", content_type='text/plain', status=500)

    return dict(
        c=client, 
        coordinates=coordinates, 
        logout_link=logout_url, 
        update_link=update_url, 
        delete_link=delete_url,
        accounts_link=accounts_url,
        )

@view_config(
    route_name='client_action', 
    match_param='action=add',
    renderer='../templates/client_modification.pt',
    )
def client_add(request):
    """ Handle new client registration
    """
    url = request.route_url('client_action', action='add', id='NEW')
    url_login = request.route_url('login')
    title = 'Registration'
    login = ''
    password = ''
    name = ''
    first_name = ''
    birth_date = ''
    address = ''
    error_msg = ''

    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']
        name = request.params['name']
        first_name = request.params['first_name']
        birth_date = request.params['birth_date']
        address = request.params['address']

        #Input validation
        error_msg = clientValidation(Client(
            login=login,
            password=password,
            name=name,
            first_name=first_name,
            birth_date=birth_date,
            address=address,
            ))

        if not error_msg:
            #Crypting password before saving it
            password=sha256((login + ':' + password).encode("utf-8")).hexdigest(), 
        
            #call Google Geocoding to fill lat & lng
            API_KEY = request.registry.settings['geocoding.API_KEY']
            url = request.route_url('geocoding_API', _query={'API_KEY':API_KEY, 'address':'\'' + address + '\''})
            geocodingInfo = urlopen(url).read()

            root = ET.fromstring(geocodingInfo.decode("utf-8"))
            status = root.find("./status").text

            #if API request successful
            if status == 'OK':
                lat = float(root.find("./result/geometry/location/lat").text)
                lng = float(root.find("./result/geometry/location/lng").text)
            else:
                lat = ''
                lng = ''

            client = Client(
                login=login,
                password=password,
                name=name,
                first_name=first_name,
                birth_date=birth_date,
                address=address,
                lat=lat,
                lng=lng,
                )

            try:
                request.dbsession.add(client)
            except DBAPIError:
                return Response("Error creating client", content_type='text/plain', status=500)

            return HTTPFound(location=url_login)

    return dict(
        url=url, 
        title=title,
        login=login,
        name=name,
        first_name=first_name,
        birth_date=birth_date,
        address=address,
        error_msg=error_msg,
        )

@view_config(
    route_name='client_action',
    match_param='action=update',
    renderer='../templates/client_modification.pt',
    permission='edit',
    )
def client_update(request):
    """ Handle client details update
    """
    clientId = request.matchdict["id"]
    if not resourceAccessAllowed(clientId, request):
        return Response("Error: Access not allowed on this resource.", content_type='text/plain', status=403)
    title = 'Client update'
    
    #pre fill form with session data
    login = request.session['client_login']
    password = ''
    name = request.session['client_name']
    first_name = request.session['client_first_name']
    birth_date = request.session['client_birth_date']
    address = request.session['client_address']
    error_msg = ''

    url_client_view = request.route_url('client_action', action='view', id=clientId)
    url = request.route_url('client_action', action='update', id=clientId)
    
    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']
        name = request.params['name']
        first_name = request.params['first_name']
        birth_date = request.params['birth_date']
        address = request.params['address']
        
        #Input validation
        error_msg = clientValidation(Client(
            login=login,
            password=password,
            name=name,
            first_name=first_name,
            birth_date=birth_date,
            address=address,
            ))

        if not error_msg:
            
            #call Google Geocoding to fill lat & lng
            API_KEY = request.registry.settings['geocoding.API_KEY']
            url = request.route_url('geocoding_API', _query={'API_KEY':API_KEY, 'address':'\'' + address + '\''})
            geocodingInfo = urlopen(url).read()

            root = ET.fromstring(geocodingInfo.decode("utf-8"))
            status = root.find("./status").text

            #if API request successful
            if status == 'OK':
                lat = float(root.find("./result/geometry/location/lat").text)
                lng = float(root.find("./result/geometry/location/lng").text)
            else:
                lat = ''
                lng = ''
            
            #Crypting password before saving it
            password=sha256((login + ':' + password).encode("utf-8")).hexdigest(), 
  
            try:
                request.dbsession.query(Client).filter(Client.id == clientId).update({
                    'login':login,
                    'password':password,
                    'name':name,
                    'first_name':first_name,
                    'birth_date':birth_date,
                    'address':address,
                    'lat':lat,
                    'lng':lng,
                    })
                transaction.commit()
            except DBAPIError:
                return Response("Error updating client", content_type='text/plain', status=500)
 
            return HTTPFound(location=url_client_view)
    
    return dict(
        url=url, 
        title=title,
        login=login,
        name=name,
        first_name=first_name,
        birth_date=birth_date,
        address=address,
        error_msg=error_msg,
        )

@view_config(
    route_name='client_action',
    match_param='action=delete',
    renderer='../templates/client_modification.pt',
    permission='edit',
    )
def client_delete(request):
    """ Delete a client and linked accounts
    """
    clientId = request.matchdict["id"]
    if not resourceAccessAllowed(clientId, request):
        return Response("Error: Access not allowed on this resource.", content_type='text/plain', status=403)

    try:
        accounts = request.dbsession.query(Account).\
            join(AccountType, Account.account_type_id == AccountType.id).\
            filter(AccountClient.client_id == clientId)
        for account in accounts:
            #delete account-client link, the account is deleted if last client using it
            deleteAccount(request.dbsession, clientId, account.id)

        request.dbsession.query(Client).filter(Client.id == clientId).delete(synchronize_session=False)

        #Log out and redirect to home
        headers = forget(request)
        url = request.route_url('login')
        return HTTPFound(location=url, headers=headers)
    except DBAPIError:
        return Response("Error deleting client", content_type='text/plain', status=500)