from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import aiohttp
import asyncio
app = FastAPI(title="world model")

# ------------ 前端静态资源配置 ------------
# 将 Vue 构建的 dist 目录挂载到 /static 路径
# app.mount("/static", StaticFiles(directory="/app/frontend/dist"), name="static")

# 在原有 CORS 配置中添加前端开发服务器地址
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Vue 开发服务器地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 根路径返回前端 index.html
@app.get("/")
async def read_index():
    return FileResponse("/app/frontend/dist/index.html")

# ------------ API 接口 ------------
class MessageRequest(BaseModel):
    content: str


async def send_to_other_server(message: str) -> dict:

    # 另一个服务器的接口地址（根据实际情况修改）
    other_server_url = "http://10.253.15.87:10002/process-message"  # 替换为实际地址
    
    try:
        # 创建异步HTTP客户端会话
        async with aiohttp.ClientSession() as session:
            # 发送POST请求到另一个服务器
            async with session.post(
                other_server_url,
                json={"message": message},  # 传递消息给另一个服务器
                timeout=600  # 超时时间（秒），防止卡住
            ) as response:
                # 检查请求是否成功（HTTP 200-299）
                if response.status not in range(200, 300):
                    raise HTTPException(
                        status_code=500,
                        detail=f"参数初始化服务器处理失败，状态码：{response.status}"
                    )
                
                # 解析返回的JSON数据
                result = await response.json()
                return result
                
    except aiohttp.ClientError as e:
        # 网络错误（如服务器不可达、超时等）
        raise HTTPException(
            status_code=503,
            detail=f"无法连接到参数初始化服务器服务器：{str(e)}"
        )
    except asyncio.TimeoutError:
        # 超时错误
        raise HTTPException(
            status_code=504,
            detail="参数初始化服务器服务器超时，请重试"
        )



@app.post("/api/chat")
async def chat(request: MessageRequest):
    user_message = request.content
    if not user_message:
        raise HTTPException(status_code=400, detail="消息内容不能为空")

    process_result = await send_to_other_server(user_message)

    if "image_urls" not in process_result:
        raise HTTPException(
            status_code=500,
            detail="处理服务器未返回有效图片image_url"
        )
    return {"reply": f"Scene Analysis:{user_message} process complete",
            "image_urls": process_result["image_urls"]
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "mode": "single-container"}


