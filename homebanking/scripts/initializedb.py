import os
import sys
import transaction

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from hashlib import sha256
    
from pyramid.scripts.common import parse_vars

from ..models.meta import Base

from ..models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    )

from ..models import (
    AccountType,
    Account,
    Client,
    AccountClient,
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)

    engine = get_engine(settings)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)

        account_type = AccountType(
            id=1, 
            label='Credit card',
            )
        dbsession.add(account_type)

        account = Account(
            id=1, 
            number='BE02001779420540', 
            balance=1250.51, 
            account_type_id=1,
            )
        dbsession.add(account)

        client = Client(
            id=1, 
            login='gilles1234', 
            password=sha256('gilles1234:password'.encode("utf-8")).hexdigest(), 
            name='Igot', 
            first_name='Gilles', 
            address='rue Georges Pochet, 4 - 5170 Lesve', 
            birth_date='19880518'
            )
        dbsession.add(client)

        client_account = AccountClient(
            client_id=1, 
            account_id=1
            )
        dbsession.add(client_account)
