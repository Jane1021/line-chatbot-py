import opencc
import logging, sys, os

s2t_converter = opencc.OpenCC('s2t')
t2s_converter = opencc.OpenCC('t2s')


def get_role_and_content(response: str):
    role = response['choices'][0]['message']['role']
    content = response['choices'][0]['message']['content'].strip()
    content = s2t_converter.convert(content)
    return role, content

def get_logger(rootName="__main__", childName="", fileName="record", timeFlag=True, log_dir="logs"):
    logName = rootName if not childName else  rootName+"."+childName
    print("Your Log name is : ", logName)
    logger = logging.getLogger(logName) 
    logger.setLevel(logging.DEBUG)
    if timeFlag:
        from datetime import datetime
        now = datetime.now()
        dt_string = now.strftime("%m%d_%H%M%S")
        fileName+="_"+dt_string
        
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)
    
    fileName = os.path.join(log_dir, fileName)

    if not childName: # 只能在最頂層加，如果每一層都這樣加，每一個 child logger 也會都 print 一行
        # file handler
        fh = logging.FileHandler(fileName+".log",mode='w', encoding='utf-8-sig')
        fh.setLevel(logging.INFO)
        ch = logging.StreamHandler() # sys.stdout
        ch.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s : %(message)s')
        # formatter = logging.Formatter('%(message)s')
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)

        # put filehandler into logger
        logger.addHandler(fh)
        logger.addHandler(ch)
    return logger