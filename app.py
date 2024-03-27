from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os

app = Flask(__name__)

line_bot_api = LineBotApi('qV1RgixFh0o0gWyljhqUfRtsiKrw5sDZXezte5VuPi6OPRxKmOSden7U48RyQAwXzlRTYSSLzBtR+likakcPU4T1P3mtBEzL6ArYuVlvybAlHhVazAbbFeQjVebao9lKCaeQXXKpJQmgj5zMb5iZ/QdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('2a607eacc549fa3782f4aa19ae0c7894')


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)
    line_bot_api.reply_message(event.reply_token, message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)