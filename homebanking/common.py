from sqlalchemy import func
from sqlalchemy.exc import DBAPIError
from .models import (
    Account,
    AccountClient,
    )

def deleteAccount(session, clientId, accountId):
    """Delete account link and account
 
    Delete the account link between client and account. This account is also
    deleted if no one else is using it.
 
    """
    try:
        session.query(AccountClient).\
            filter(AccountClient.client_id == clientId, AccountClient.account_id == accountId).\
            delete(synchronize_session=False)
            
        linkToOtherClient = session.query(func.count(AccountClient.account_id)).\
            filter(AccountClient.account_id == accountId).scalar()

        if not linkToOtherClient:
            session.query(Account).\
                filter(Account.id == accountId).\
                delete(synchronize_session=False)
    except DBAPIError:
        return Response("Error deleting account", content_type='text/plain', status=500)