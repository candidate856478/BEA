from pyramid.security import Allow, Everyone
 
class Root(object):
    __acl__ = [
                (Allow, 'editor', 'edit'),
                (Allow, 'editor', 'view'),
                (Allow, 'auditor', 'view'),
              ] 
 
    def __init__(self, request):
        pass