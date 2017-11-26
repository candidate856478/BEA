from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.session import UnencryptedCookieSessionFactoryConfig

from .security import (
    groupfinder,
    )

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    #Setting authorization and authentication policies
    authn_policy = AuthTktAuthenticationPolicy(
            settings['homebanking.secret'],
            callback=groupfinder,
            hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()

    session_factory = UnencryptedCookieSessionFactoryConfig('s3cr3t')
    
    config = Configurator(
        settings=settings,
        root_factory='.resources.Root',
        session_factory=session_factory,
        )

    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    config.include('pyramid_chameleon')
    config.include('pyramid_jinja2')
    config.include('.models')
    config.include('.routes')
    config.scan()
    return config.make_wsgi_app()
