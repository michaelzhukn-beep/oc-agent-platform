import os
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
import json
from fastapi import FastAPI,HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware


#加载 .env中的环境变量
load_dotenv()

#创建有一个对话接口
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

SYSTEM_TEMPLATE = """你是{name},性别是{gender}.
性格：{personality},
说话方式：{speaking_style},
背景故事:{backstory}

请始终以{name}的身份回复,保持角色一致性。回复控制在60字以内"""

class ChatRequest(BaseModel):
    message:str
    character:str
    session_id:str

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
sessions = {}

@app.get("/characters")
def list_character():
    files = os.listdir("characters")
    characters = []
    for file in files:
        characters.append(file.replace(".json",""))
    return {"character": characters}

@app.post("/chat")
def chat(request:ChatRequest):
    
    filename = "characters/" + request.character + ".json"
    if not os.path.exists(filename):
        raise HTTPException(status_code=404,detail="角色不存在")
    with open(filename, "r",encoding="utf-8") as f:
        characterinfo = json.load(f)
    required_fields=["name","gender","personality","speaking_style","backstory"]
    for field in required_fields:
        if field not in characterinfo:
            raise HTTPException(status_code=400,detail=f"角色卡缺少字段{field}")
            
    system_prompt  = SYSTEM_TEMPLATE.format(**characterinfo)
    
    if request.session_id not in sessions:
        sessions[request.session_id] = [
            {"role":"system","content":system_prompt}
]
    message = sessions[request.session_id]
    message.append({"role":"user","content":request.message})
    
    response = client.chat.completions.create(
        model = "deepseek-chat",
        messages = message,
        max_tokens=100,
        stream=True
)
    
    def generate():
        reply=""
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                reply += content
                yield content
        message.append({"role":"assistant","content":reply})
    return StreamingResponse(generate(),media_type="text/event-stream")   
        
    


