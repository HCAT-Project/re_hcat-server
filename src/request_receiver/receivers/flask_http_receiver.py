#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#  Copyright (C) 2023. HCAT-Project-Team
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
@File       : flask_http_receiver.py

@Author     : hsn

@Date       : 4/15/23 12:01 PM

@Version    : 1.0.0
"""
import os

from flask import Flask, send_from_directory, request
from flask_cors import CORS
from gevent import pywsgi
from src.util import request_parse
from src.containers import Request, ReturnData
from src.request_receiver.base_receiver import BaseReceiver


class FlaskHttpReceiver(BaseReceiver):
    def _start(self):
        self.app = Flask(__name__)
        self.app.config['UPLOAD_FOLDER'] = self.config.get('sys', {}).get('upload_folder', 'static/files')
        self.app.config['MAX_CONTENT_LENGTH'] = self.config.get('sys', {}).get('max_content_length', 16 * 1024 * 1024)

        # Enable Cross-Origin Resource Sharing (CORS)
        if self.config.get_from_pointer('/receivers/FlaskHttpReceiver/enable-cors', True):
            CORS(self.app, supports_credentials=True)
        # optional, but recommended
        if self.config.get_from_pointer('/receivers/FlaskHttpReceiver/enable-static', True):
            @self.app.route('/<path:path>', methods=['GET', 'POST'])
            def send_static(path):
                folder = self.config.get_from_pointer('/receivers/FlaskHttpReceiver/enable-static', 'static')
                return send_from_directory(os.path.join(os.getcwd(), folder), path)

        @self.app.route('/api/<path:path>', methods=['GET', 'POST'])
        def recv(path):
            req = Request(path, request_parse(request), request.cookies)
            rt = self.create_req(req)

            if isinstance(rt, ReturnData):
                rt = rt.jsonify()
            elif rt is None:
                rt = ReturnData(ReturnData.NULL, '').jsonify()
            return rt

        server = pywsgi.WSGIServer((self.host, self.port), self.app)
        self.wsgi_server = server
        server.serve_forever()
