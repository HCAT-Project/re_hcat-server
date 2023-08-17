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
@File       : regex.py

@Author     : hsn

@Date       : 3/12/23 10:01 AM

@Version    : 1.0.0
"""

# regex for email address
regex_email = r'^[\w.%+-]+@(gmail\.com|yahoo\.com|msn\.com|hotmail\.com|aol\.com|ask\.com|live\.com|qq\.com|0355\.net' \
              r'|163\.com|163\.net|263\.net|3721\.net|yeah\.net|googlemail\.com|mail\.com|aim\.com|walla\.com|inbox' \
              r'\.com|126\.com|sina\.com|21cn\.com|sohu\.com|yahoo\.com\.zh_CN|tom\.com|etang\.com|eyou\.com|56\.com|' \
              r'x' \
              r'\.zh_CN|chinaren\.com|sogou\.com|citiz\.com|hongkong\.com|ctimail\.com|hknet\.com|netvigator\.com|' \
              r'mail' \
              r'\.hk\.com|swe\.com\.hk|ITCCOLP\.COM\.HK|BIZNETVIGATOR\.COM|SEED\.NET\.TW|TOPMARKEPLG\.COM\.TW|PCHOME' \
              r'\.COM\.TW|hinet\.net\.tw|cyber\.net\.pk|omantel\.net\.om|libero\.it|webmail\.co\.za|xtra\.co\.nz' \
              r'|pacific\.net\.sg|FASTMAIL\.FM|emirates\.net\.ae|eim\.ae|net\.sy|scs-net\.org|mail\.sy|ttnet\.net\.tr' \
              r'|superonline\.com|yemen\.net\.ye|y\.net\.ye|cytanet\.com\.cy|aol\.com|netzero\.net|twcny\.rr\.com' \
              r'|comcast\.net|warwick\.net|cs\.com|verizon\.net|bigpond\.com|otenet\.gr|vsnl\.com|wilnetonline\.net' \
              r'|cal3\.vsnl\.net\.in|rediffmail\.com|sancharnet\.in|NDF\.VSNL\.NET\.IN|DEL3\.VSNL\.NET\.IN|xtra\.co' \
              r'\.nz|yandex\.ru|t-online\.de|NETVISION\.NET\.IL|BIGPOND\.NET\.AU|MAIL\.RU|EV|ADSL\.LOXINFO\.COM|SCS' \
              r'-NET\.ORG|EMIRATES\.NET\.AE|QUALITYNET\.NET|ZAHAV\.NET\.IL|netvision\.net\.il|xx\.org\.il|hn\.vnn\.vn' \
              r'|hcm\.fpt\.vn|hcm\.vnn\.vn|candel\.co\.jp|zamnet\.zm|amet\.com\.ar|infovia\.com\.ar|mt\.net\.mk' \
              r'|sotelgui\.net\.gn|prodigy\.net\.mx|citechco\.net|xxx\.meh\.es|terra\.es|wannado\.fr|mindspring\.com' \
              r'|excite\.com|africaonline\.co\.zw|samara\.co\.zw|zol\.co\.zw|mweb\.co\.zw|aviso\.ci|africaonline\.co' \
              r'\.ci|afnet\.net|mti\.gov\.na|namibnet\.com|iway\.na|be-local\.com|infoclub\.com\.np)$'

name_regex = r'^[a-zA-Z][a-zA-Z0-9_]{4,15}$'
gender_regex = r'^[a-zA-Z0-9_]{0,24}$'
bio_regex = r'^[a-zA-Z0-9_]{0,24}$'
bio_invalid_regex = r'\pC'
