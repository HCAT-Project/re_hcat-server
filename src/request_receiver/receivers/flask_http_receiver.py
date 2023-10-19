#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#  Copyright (C) 2023. HCAT-Project-Team
#  _
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  _
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#  _
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
@File       : flask_http_receiver.py

@Author     : hsn

@Date       : 4/15/23 12:01 PM

@Version    : 1.0.0
"""
import logging
from pathlib import Path

from flask import Flask, send_from_directory, request
from flask_cors import CORS
from gevent import pywsgi

from src.containers import Request, ReturnData
from src.request_receiver.base_receiver import BaseReceiver
from src.util import request_parse
from src.util.i18n import gettext_func as _


class FlaskHttpReceiver(BaseReceiver):
    def _start(self):
        self.app = Flask(__name__)
        self.app.config["UPLOAD_FOLDER"] = self.global_config.get_from_pointer(
            "/network/upload/upload_folder", "static/files"
        )
        self.app.config["MAX_CONTENT_LENGTH"] = self.global_config.get_from_pointer(
            "/network/upload/max_content_length", 16 * 1024 * 1024
        )

        # Enable Cross-Origin Resource Sharing (CORS)
        if self.receiver_config.get_from_pointer("enable-cors", True):
            CORS(self.app, supports_credentials=True)
        # optional, but recommended
        if self.receiver_config.get_from_pointer("enable-static", True):

            @self.app.route("/", methods=["GET"])
            @self.app.route("/<path:path>", methods=["GET"])
            def send_static(path=None):
                static_folder = self.receiver_config.get_from_pointer(
                    "static-folder", "static"
                )
                if path is None or (not (Path.cwd() / static_folder / path).exists()):
                    path = "index.html"

                return send_from_directory(Path.cwd() / static_folder, path)

        @self.app.route("/api/<path:path>", methods=["GET", "POST"])
        def recv(path):
            req = Request(
                path=path,
                data=request_parse(request),
                files=request.files,
                cookies=request.cookies,
                headers=request.headers,
            )
            rt = self.create_req(req)

            if isinstance(rt, ReturnData):
                rt_resp = rt.flask_respify()
            elif rt is None:
                rt_resp = ReturnData(ReturnData.NULL, "").flask_respify()
            else:
                raise TypeError(
                    f"Return type of {type(self).__name__} must be ReturnData or None, not {type(rt)}"
                )

            # [High severity]CVE-2023-30861: Flask vulnerable to possible disclosure of permanent session cookie due
            # to missing Vary: Cookie header
            if "_cookie" in rt.json_data:
                rt_resp.headers.add("Vary", "Cookie")

            return rt_resp

        # ssl
        ssl_kwargs = {}
        if self.global_config.get_from_pointer("/network/ssl/enable", False):
            ssl_cert = self.global_config.get_from_pointer("/network/ssl/cert")
            ssl_key = self.global_config.get_from_pointer("/network/ssl/key")
            ssl_kwargs = {"keyfile": ssl_key, "certfile": ssl_cert}
            self.logger.debug(_("FlaskHttpReceiver started with SSL."))

        server = pywsgi.WSGIServer((self.host, self.port), self.app, **ssl_kwargs)
        self.wsgi_server = server

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            server.close()
            logging.info(_("FlaskHttpReceiver stopped."))
