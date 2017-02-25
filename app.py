# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

from __future__ import unicode_literals

import os
import sys
import random
from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

port = os.getenv('PORT', 8000)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)
state = 'Hoge'


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    print(state)

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    texts = ['アウーズビッラーヒ　ミナッシャイフォーニャッラジーム', 'アルハムドゥリッラーヒ　ラッビルアーラミーン',
             'アーッラハマーニッラヒーム', 'マーリキ　ヤウミッディーン', 'イィヤーカナアブドゥ　ワイィヤーカナスタイーン',
             'イヒディナッスィラータ（ル）　ムスタキーム', 'スィラータッラズィーナ アンアムタアライヒーム '
             + 'ガイ（ル）リィルマグドゥービ　アライヒーム ワラッ　ダァーーッリーーィン',
             'アーメン']
    alabia = ['بِسْمِ اللّهِ الرَّحْمـَنِ الرَّحِيم', 'الْحَمْدُ للّهِ رَبِّ الْعَالَمِين', 'الرَّحمـنِ الرَّحِيم'
              'مَـالِكِ يَوْمِ الدِّين', 'إِيَّاك نَعْبُدُ وإِيَّاكَ نَسْتَعِين', 'اهدِنَــــا الصِّرَاطَ المُستَقِيمَ',
              'صِرَاطَ الَّذِينَ أَنعَمتَ عَلَيهِمْ غَيرِ المَغضُوبِ عَلَيهِمْ وَلاَ الضَّالِّين', 'آمين']

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)


    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        state = "Geff"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=random.choice(texts))
        )

    return 'OK'


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=port, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(host='0.0.0.0', debug=options.debug, port=options.port)
