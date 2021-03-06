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
import json
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
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

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


class UserInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100))
    mode = db.Column(db.Integer)
    last_one = db.Column(db.Integer)
    
    def __init__(self, user_id, mode, last_one):
        self.mode = mode
        self.user_id = user_id
        self.last_one = last_one


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    texts = ['アウーズビッラーヒ　ミナッシャイフォーニャッラジーム', 'アルハムドゥリッラーヒ　ラッビルアーラミーン',
             'アーッラハマーニッラヒーム', 'マーリキ　ヤウミッディーン', 'イィヤーカナアブドゥ　ワイィヤーカナスタイーン',
             'イヒディナッスィラータ（ル）　ムスタキーム', 'スィラータッラズィーナ アンアムタアライヒーム '
             + 'ガイ（ル）リィルマグドゥービ　アライヒーム ワラッ　ダァーーッリーーィン',
             'アーメン']
    alabia = ['بِسْمِ اللّهِ الرَّحْمـَنِ الرَّحِيم', 'الْحَمْدُ للّهِ رَبِّ الْعَالَمِين', 'الرَّحمـنِ الرَّحِيم'
              'مَـالِكِ يَوْمِ الدِّين', 'إِيَّاك نَعْبُدُ وإِيَّاكَ نَسْتَعِين', 'اهدِنَــــا الصِّرَاطَ المُستَقِيمَ',
              'صِرَاطَ الَّذِينَ أَنعَمتَ عَلَيهِمْ غَيرِ المَغضُوبِ عَلَيهِمْ وَلاَ الضَّالِّين',
              'آمين']
    mean = ['神の御名の下に最高の慈悲を', '全ての感謝は世界の神アッラーただ一人へ', 'アッラーは最高の慈悲を持ち',
            '最後の審判の日の支配者である', '我々はあなたのみを崇拝し、あなたのみに助けを求める',
            '我々全てを正しい道に導きたまえ',
            'あなたの怒りを与えられた者や自分の道を見失った者ではなく、あなたの恩寵を授けられた者の道',
            'アーメン']
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
        if event.source.type != 'user':
            continue
        
        print(event.source.sender_id)
        get_id = event.source.sender_id
        # DBからuseridを検索してくる
        user_info = UserInfo.query.filter_by(user_id=get_id).first()
        
        # もしなければDBに登録
        if user_info is None:
            user_info = UserInfo(event.source.sender_id, 0, 0)
            db.session.add(user_info)
            obj = texts
        
        # ある場合はmodeを選択
        else:
            if user_info.mode == 1:
                obj = texts
            else:
                obj = alabia
                
            # アラビア, 日本語の場合モード切り替え
            if event.message.text == 'アラビア語モード':
                user_info.mode = 0
                obj = alabia
            elif event.message.text == '日本語モード':
                user_info.mode = 1
                obj = texts
            
                
        if event.message.text == '意味は？' or event.message.text == 'どういう意味？':
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=mean[user_info.last_one])
            )
        elif event.message.text == '日本語では？':
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=texts[user_info.last_one])
            )
        elif event.message.text == 'アラビア語では？':
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=alabia[user_info.last_one])
            )
        else:
            rand = random.randint(0, len(obj)-1)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=obj[rand])
            )
            user_info.last_one = rand
        
        db.session.commit()

            
            

        
        

    return 'OK'


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=port, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(host='0.0.0.0', debug=options.debug, port=options.port)
