#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import os.path
import sys
import argparse

import cherrypy
from cherrypy.process import plugins
from cherrypy.lib import static
from cherrypy.process.wspbus import Bus

from httplogger import HTTPLogger

sys.path.append(os.path.dirname(__file__))

from core.base.setup import Settings

__all__ = ['DjangoAppPlugin']


class DjangoAppPlugin(plugins.SimplePlugin):

    def __init__(self, bus: Bus, settings_module: str = 'settings',
                 wsgi_http_logger: type = HTTPLogger,
                 local_settings: Settings = None) -> None:
        """ CherryPy engine plugin to configure and mount
        the Django application onto the CherryPy server.
        """
        plugins.SimplePlugin.__init__(self, bus)
        self.settings_module = settings_module
        self.wsgi_http_logger = wsgi_http_logger
        self.crawler_settings = local_settings

    def start(self) -> None:
        """ When the bus starts, the plugin is also started
        and we load the Django application. We then mount it on
        the CherryPy engine for serving as a WSGI application.
        We let CherryPy serve the application's static files.
        """
        from frontend import settings
        settings.crawler_settings = self.crawler_settings

        os.environ['DJANGO_SETTINGS_MODULE'] = self.settings_module

        from django.core.wsgi import get_wsgi_application

        def corsstaticdir(
                section: str, dir: str, root: str = '', match: str = '',
                content_types: None = None, index: str = '', debug: bool = False
        ) -> bool:
            cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
            return static.staticdir(section, dir, root, match, content_types, index, debug)

        cherrypy.tree.graft(self.wsgi_http_logger(get_wsgi_application(), self.crawler_settings))

        settings.WORKERS.start_workers(settings.CRAWLER_SETTINGS)

        tool = cherrypy._cptools.HandlerTool(corsstaticdir)
        static_handler = tool.handler(
            section="/",
            dir=os.path.split(settings.STATIC_ROOT)[1],
            root=os.path.abspath(os.path.split(settings.STATIC_ROOT)[0])
        )
        cherrypy.tree.mount(static_handler, settings.STATIC_URL)

        media_handler = tool.handler(
            section="/",
            dir=os.path.split(settings.MEDIA_ROOT)[1],
            root=os.path.abspath(os.path.split(settings.MEDIA_ROOT)[0])
        )
        cherrypy.tree.mount(media_handler, settings.MEDIA_URL)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='PandaServer')

    parser.add_argument('-c', '--config-dir',
                        required=False,
                        action='store',
                        help='Directory to store configuration files. (database, logs, configuration file)')

    parser.add_argument('-p', '--port',
                        type=int,
                        required=False,
                        action='store',
                        help='Override port.')

    parser.add_argument('-d', '--daemonize',
                        required=False,
                        action='store_true',
                        default=False,
                        help='Run the server as a daemon.')

    parser.add_argument('-pf', '--pidfile',
                        required=False,
                        action='store',
                        default=None,
                        help='Store the process id in the given file.')

    args = parser.parse_args()

    if args.config_dir:
        crawler_settings = Settings(load_from_disk=True, default_dir=args.config_dir)
        os.environ['PANDA_CONFIG_DIR'] = args.config_dir
    else:
        crawler_settings = Settings(load_from_disk=True)

    if args.port:
        cherrypy_port = args.port
    else:
        cherrypy_port = crawler_settings.webserver.bind_port

    cherrypy_settings = {
        'server.socket_host': crawler_settings.webserver.bind_address,
        'server.socket_port': cherrypy_port,
        'checker.on': False,
        'engine.autoreload.on': crawler_settings.cherrypy_auto_restart,
    }

    if crawler_settings.webserver.enable_ssl:
        cherrypy_settings.update({
            'server.ssl_module': 'builtin',
            'server.ssl_certificate': crawler_settings.webserver.ssl_certificate,
            'server.ssl_private_key': crawler_settings.webserver.ssl_private_key,
        })

    cherrypy.config.update(cherrypy_settings)

    user_handler = cherrypy.process.plugins.SignalHandler(cherrypy.engine)
    user_handler.handlers['SIGUSR2'] = cherrypy.engine.restart

    # SIGTERM exits, SIGUSR2 forces restart.
    cherrypy.engine.signal_handler = user_handler

    if args.daemonize:
        # TODO: Daemonizing is stopping the start_workers method form starting workers on startup. Maybe use ready()
        cherrypy.config.update({'log.screen': False})
        plugins.Daemonizer(cherrypy.engine).subscribe()

    if args.pidfile:
        plugins.PIDFile(cherrypy.engine, args.pidfile).subscribe()

    DjangoAppPlugin(cherrypy.engine,
                    settings_module='frontend.settings',
                    local_settings=crawler_settings).subscribe()

    cherrypy.log(
        "Loading and serving Panda Backup. Listening on " +
        crawler_settings.webserver.bind_address + ":" +
        str(cherrypy_port)
    )

    cherrypy.quickstart()