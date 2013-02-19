import logging

from pyramid.config import Configurator
from pyramid.events import subscriber, NewRequest
from pyramid.tweens import EXCVIEW
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    DBSession2,
    Base,
    )

log = logging.getLogger(__name__)

@subscriber(NewRequest)
def new_request_subscriber(event):
    event.request.add_finished_callback(log_callback)

def log_callback(request):
    log.info("In commit callback. Req {rid} was for {path}"
             .format(rid=str(id(request)), path=request.path_qs))
    session = request.db
    try:
        # If one of the tweens has already rolled back the session (for
        # example, due to an exception), this commit will be a no-op. It will
        # not, under normal circumstances, raise another exception.
        session.commit()
    except Exception as e:
        log.info("commit callback: commit raised exception")
        session.rollback()
        raise
    finally:
        log.info("commit callback: removing session")
        session.remove()

def tween_factory_1(handler, registry):
    def txn_tween(request):
        log.info("in tween factory 1")
        try:
            return handler(request)
        except:
            log.info("tween factory 1 exception")
            request.db.rollback()
            raise

    return txn_tween

def tween_factory_2(handler, registry):
    def log_tween(request):
        log.info("in tween factory 2")
        try:
            return handler(request)
        except:
            log.info("tween factory 2 exception")
            raise
    return log_tween

from pyramid.decorator import reify
from pyramid.request import Request
class TTRequest(Request):
    @reify
    def db(self):
        DBSession()
        session = DBSession
        return session

    @reify
    def db2(self):
        DBSession2()
        session = DBSession2
        return session

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings, request_factory=TTRequest)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_tween('tweentester.tween_factory_1', under=EXCVIEW)
    config.add_tween('tweentester.tween_factory_2', under=EXCVIEW)
    config.scan()
    return config.make_wsgi_app()
