import os
import dotenv

DIR = os.path.dirname(os.path.realpath(__file__))

def p(name: str) -> str:
    return os.path.join(DIR, name)


ENV = dotenv.dotenv_values(p('.env'))
MIDDLEWARE = dotenv.dotenv_values(p('.middleware.env'))
DB = dotenv.dotenv_values(p('.database.env'))
MICRO = dotenv.dotenv_values(p('.micro.env'))

class MiddlewareEnv:
    MAX_CONTENT_SIZE = int(MIDDLEWARE.get('MAX_CONTENT_SIZE', None) or 3145728)
    INTERNAL_IPS = [i.split('.') for i in (MIDDLEWARE.get('INTERNAL_IPS', None) or '').split(',')]
    INTERNAL_ROUTE_PREFIXES = (MIDDLEWARE.get('INTERNAL_ROUTE_PREFIXES', None) or '').split(',')


class DatabaseEnv:
    ECHO = (DB.get('ECHO', None) or 'false').lower() == 'true'

    HOST = DB['HOST']
    PORT = int(DB.get('PORT') or 3306)
    USERNAME = DB['USERNAME']
    PASSWORD = DB['PASSWORD']
    DATABASE = DB['DATABASE']

class MicroEnv:
    CDN = MICRO.get('CDN', 'localhost:5001')
    AUTH = MICRO.get('AUTH', 'localhost:5002')
    
class Env:
    HOST = ENV.get('HOST', None) or 'localhost'
    PORT = int(ENV.get('PORT', None) or '5002')
    DEBUG = (ENV.get('DEBUG', None) or 'false').lower() == 'true'