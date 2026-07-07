import os
os.system("prisma generate")


from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from prisma import Prisma
import uvicorn
import urllib.parse

app = FastAPI()
prisma = Prisma()
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup():
    await prisma.connect()

@app.on_event("shutdown")
async def shutdown():
    await prisma.disconnect()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/enviar-orcamento")
async def enviar_orcamento(
    nome: str = Form(...), 
    whatsapp: str = Form(...), 
    aparelho: str = Form(...), 
    defeito: str = Form(...)
):
    # Preço inicial zerado para você avaliar depois no seu painel
    preco = 0.0
    tempo = "A avaliar"
    
    # Salva no banco de dados da Neon
    await prisma.orcamento.create(
        data={
            "nomeCliente": nome,
            "whatsapp": whatsapp,
            "aparelho": aparelho,
            "defeito": defeito,
            "precoEst": preco,
            "tempoEst": tempo
        }
    )
    
    # Formata a notificação para o seu WhatsApp
    texto_msg = (
        f"🛠️ *Novo Orçamento - Lange Reparos*\n\n"
        f"👤 *Cliente:* {nome}\n"
        f"📱 *Aparelho:* {aparelho}\n"
        f"❌ *Defeito Relatado:* {defeito}\n\n"
        f"Aguardando análise técnica!"
    )
    
    msg_codificada = urllib.parse.quote(texto_msg)
    
    # IMPORTANTE: Coloque aqui o seu número real com DDD (Ex: 5547999999999)
    seu_numero = "5547999999999" 
    
    return RedirectResponse(url=f"https://wa.me/{seu_numero}?text={msg_codificada}", status_code=303)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)