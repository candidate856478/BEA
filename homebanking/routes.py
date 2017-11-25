def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('login', '/')
    config.add_route('logout', '/logout')
    config.add_route('client_action', '/client/{action}/{id}')
    config.add_route('account_list', '/client/{clientId}/account/')
    config.add_route('account_action', '/client/{clientId}/account/{action}/{id}')
    config.add_route('geocoding_API', 'http://maps.googleapis.com/maps/api/geocode/xml')