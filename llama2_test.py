
import os
from distutils.util import strtobool

from flask import Flask, abort, request
from langchain.chains import ConversationalRetrievalChain
from langchain.llms import LlamaCpp  # 修改成LlamaCpp
from langchain_community.embeddings import LlamaCppEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores.chroma import Chroma  # 修改成Chroma
from linebot import LineBotApi, WebhookHandler, WebhookParser
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from opencc import OpenCC

import src.constants as const
import src.utils as utils
#from src.utils import get_logger

from logging import getLogger
logger = getLogger(__name__)

# logger and const
#logger = get_logger(__name__)
#encoding_model_name = const.ENCODING_MODEL_NAME

# get channel_secret and channel_access_token from your environment variable

from dotenv import load_dotenv

# 加載 .env 文件中的環境變數
load_dotenv()

channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)

# multi-lingual support
support_multilingual = False


# configure_retriever
def configure_retriever():
    global embeddings
    logger.info("Configuring retriever")
    embeddings = LlamaCppEmbeddings(
        model_path="D:\\Users\\user\\Desktop\\專題\\llama-2-7b-chat.Q4_0.gguf"
    )

    

    vectordb = Chroma(  # 修改成Chroma
        persist_directory="D:\\Users\\user\\Desktop\\專題\\文字檔txt\\",
        embedding_function=embeddings.embed_query
    
    )
    
    retriever = vectordb.as_retriever(
        search_type="mmr", search_kwargs={"k": 10}
    )

    

    logger.info("configuring retriever done")
    return retriever

# create app
app = Flask(__name__)
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)
parser = WebhookParser(channel_secret)

# initialize agent and retriever
llm = LlamaCpp(  # 修改成LlamaCpp
    model_path="D:\\Users\\user\\Desktop\\專題\\llama-2-7b-chat.Q4_0.gguf",
    device='cpu',  # 使用CPU，若有GPU可改為 'cuda'
)

# configure retriever
retriever = configure_retriever()

# create converter (simple chinese to traditional chinese)
s2t_converter = OpenCC("s2t")

# create memory
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    input_key="question",
    output_key="answer",
)

# use PromptTemplate to generate prompts
qa_chain = ConversationalRetrievalChain.from_llm(
    llm,
    retriever=retriever,
    memory=memory,
    verbose=True,
    return_source_documents=True,
)

# create handlers
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try: 
        handler.handle(body, signature)

    except Exception as e:
        logger.error(e)
        abort(400)

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global embeddings
    question = event.message.text.strip()

    if question.startswith("/清除") or question.lower().startswith("/clear"):
        memory.clear()
        answer = "歷史訊息清除成功"
    elif (
        question.startswith("/教學")
        or question.startswith("/指令")
        or question.startswith("/說明")
        or question.startswith("/操作說明")
        or question.lower().startswith("/instruction")
        or question.lower().startswith("/help")
    ):
        answer = "指令：\n/清除 or /clear\n👉 當 Bot 開始鬼打牆，可清除歷史訊息來重置"
    else:
        question_embedding = embeddings.embed_query(question, sequence_pooling="mean")
        # get answer from qa_chain
        response = qa_chain.predict({"question": question_embedding})
        answer = response["answer"]
        answer = s2t_converter.convert(answer)
        logger.info(f"answer: {response}")

    # select most related docs and get video id
    ref_video_template = ""
    for i in range(min(const.N_SOURCE_DOCS, len(response["source_documents"]))):
        most_related_doc = response["source_documents"][i]
        most_related_video_id = most_related_doc.metadata["video_id"]
        url = f"https://www.youtube.com/watch?v={most_related_video_id}"
        ref_video_template = f"{ref_video_template}\n{url}"

    # add reference video
    answer = f"{answer}\n\nSource: {ref_video_template}"

    # reply message
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=answer))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

    logger.info("app started")
