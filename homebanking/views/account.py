import transaction
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from sqlalchemy.exc import DBAPIError
from random import randrange
from ..security import resourceAccessAllowed
from ..models import (
    Account,
    AccountClient,
    AccountType,
    )
from ..common import deleteAccount

@view_config(
    route_name='account_list',
    renderer='../templates/account_list.pt',
    permission='edit',
    )
def account_list(request):
    """ List all accounts for a given client
    """
    clientId = request.matchdict["clientId"]
    if not resourceAccessAllowed(clientId, request):
        return Response("Error: Access not allowed on this resource.", content_type='text/plain', status=403)
    url_client_view = request.route_url('client_action', action='view', id=clientId)
    url_account_add = request.route_url('account_action', clientId=clientId, action='add', id='NEW')
    url_account_del = request.route_url('account_action', clientId=clientId, action='delete', id='')
    url_account_upd = request.route_url('account_action', clientId=clientId, action='update', id='')
    accounts = {}

    try:
        accounts = request.dbsession.query(Account, AccountType, AccountClient).\
            join(AccountType, Account.account_type_id == AccountType.id).\
            join(AccountClient, Account.id == AccountClient.account_id).\
            filter(AccountClient.client_id == clientId)
            
        types = request.dbsession.query(AccountType)
    except DBAPIError:
        return Response("Error retrieving accounts", content_type='text/plain', status=500)

    return dict(
        accounts=accounts,
        back=url_client_view,
        add_account=url_account_add,
        del_account=url_account_del,
        upd_account=url_account_upd,
        types=types,
        )

@view_config(
    route_name='account_action',
    renderer='../templates/account_update.pt',
    match_param='action=add',
    permission='edit',
    )
def account_add(request):
    """ Handle account creation
    """
    clientId = request.matchdict["clientId"]
    if not resourceAccessAllowed(clientId, request):
        return Response("Error: Access not allowed on this resource.", content_type='text/plain', status=403)
    accounts_url = request.route_url('account_list', clientId=clientId)

    if 'form.submitted' in request.params:
        type = request.params['account_type']
        
        try:
            #random IBAN generation
            baseValue = randrange(1000) + 1
            baseValue *= 97
            iban = str(baseValue)
            while len(iban) < 12:
                iban = '0' + iban
            iban = 'BE54' + iban
            
            #DB account creation
            account = Account(number=iban, balance=0.0, account_type_id=type)
            request.dbsession.add(account)
            #flush and refresh session to get generated id
            request.dbsession.flush()
            request.dbsession.refresh(account)

            #DB account-client link creation
            accountClient = AccountClient(client_id=clientId, account_id=account.id)
            request.dbsession.add(accountClient)
        except DBAPIError:
            return Response("Error creating new account", content_type='text/plain', status=500)

    return HTTPFound(location=accounts_url)
    
@view_config(
    route_name='account_action',
    renderer='../templates/account_update.pt',
    match_param='action=delete',
    permission='edit',
    )
def account_delete(request):
    """ Suppression of the account link for current client
    
        Account will also be deleted if no other client linked to it
    """
    clientId = request.matchdict["clientId"]
    if not resourceAccessAllowed(clientId, request):
        return Response("Error: Access not allowed on this resource.", content_type='text/plain', status=403)
    accountId = request.matchdict["id"]
    accounts_url = request.route_url('account_list', clientId=clientId)

    deleteAccount(request.dbsession, clientId, accountId)

    return HTTPFound(location=accounts_url)
    
@view_config(
    route_name='account_action',
    renderer='../templates/account_update.pt',
    match_param='action=update',
    permission='edit',
    )
def account_update(request):
    """ Handle money deposit/withdrawal for a given account
    """
    clientId = request.matchdict["clientId"]
    if not resourceAccessAllowed(clientId, request):
        return Response("Error: Access not allowed on this resource.", content_type='text/plain', status=403)
    accountId = request.matchdict["id"]
    accounts_url = request.route_url('account_list', clientId=clientId)
    url_account_upd = request.route_url('account_action', clientId=clientId, action='update', id=accountId)
    title='Money withdrawal/deposit'
    error_msg=''
    
    try:
        account = request.dbsession.query(Account).filter(Account.id == accountId).first()
    except DBAPIError:
        return Response("Error retrieving account", content_type='text/plain', status=500)

    if 'form.submitted' in request.params:
        #add/remove money from account balance
        money_transfer = request.params['money_transfer']
        total = float(account.balance) + float(money_transfer)

        if not error_msg:  
            try:
                request.dbsession.query(Account).filter(Account.id == accountId).update({
                    'balance':total,
                    })
                transaction.commit()
            except DBAPIError:
                return Response("Error updating account", content_type='text/plain', status=500)

            return HTTPFound(location=accounts_url)

    return dict(
        url=url_account_upd,
        back=accounts_url,
        title=title,
        error_msg=error_msg,
        accountNumber=account.number,
        )