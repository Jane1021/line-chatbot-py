from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os


app = Flask(__name__)

line_bot_api = LineBotApi('qV1RgixFh0o0gWyljhqUfRtsiKrw5sDZXezte5VuPi6OPRxKmOSden7U48RyQAwXzlRTYSSLzBtR+likakcPU4T1P3mtBEzL6ArYuVlvybAlHhVazAbbFeQjVebao9lKCaeQXXKpJQmgj5zMb5iZ/QdB04t89/1O/w1cDnyilFU=')  # 可在無法取得值時返回異常
handler = WebhookHandler('2a607eacc549fa3782f4aa19ae0c7894')  # 可在無法取得值時返回異常


@app.route("/callback", methods=['POST'])
def callback():
    # 抓 X-Line-Signature 標頭的值
    signature = request.headers['X-Line-Signature']
    # 抓 request body 的文字
    body = request.get_data(as_text=True)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


@handler.add(MessageEvent, message=(TextMessage))
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text)
    )
    return


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))