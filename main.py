import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from prisma import Prisma

# 1. Inicializa o cliente Prisma
prisma = Prisma(datasource={
    'url': 'postgresql://neondb_owner:npg_MFJYGyhju41W@ep-still-mouse-acd1nsal-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
})

# 2. Gerencia o ciclo de vida
@asynccontextmanager
async def lifespan(app: FastAPI):
    await prisma.connect()
    yield
    if prisma.is_connected():
        await prisma.disconnect()

app = FastAPI(lifespan=lifespan)

# 3. Rota Inicial (Formulário de Cadastro)
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head>
            <title>Lange Reparos - Novo Orçamento</title>
            <meta charset="utf-8">
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; }
                .container { max-width: 500px; background: white; padding: 30px; margin: 40px auto; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
                h2 { text-align: center; color: #333; margin-bottom: 20px; }
                label { font-weight: bold; color: #555; display: block; margin-top: 10px; }
                input, select { width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
                button { width: 100%; background-color: #28a745; color: white; padding: 12px; border: none; border-radius: 4px; font-size: 16px; font-weight: bold; margin-top: 20px; cursor: pointer; }
                button:hover { background-color: #218838; }
                .link-painel { display: block; text-align: center; margin-top: 15px; color: #007bff; text-decoration: none; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>🛠️ Novo Orçamento - Lange Reparos</h2>
                <form action="/enviar-orcamento" method="POST">
                    <label>Nome do Cliente:</label>
                    <input type="text" name="nomeCliente" required>

                    <label>WhatsApp:</label>
                    <input type="text" name="whatsapp" placeholder="(47) 99999-9999" required>

                    <label>Aparelho / Modelo:</label>
                    <input type="text" name="aparelho" placeholder="Ex: iPhone 11, Moto G20" required>

                    <label>Defeito:</label>
                    <input type="text" name="defeito" placeholder="Ex: Tela quebrada, Conector de carga" required>

                    <label>Preço Estimado (R$):</label>
                    <input type="number" step="0.01" name="precoEst" required>

                    <label>Tempo Estimado:</label>
                    <input type="text" name="tempoEst" placeholder="Ex: 2 horas, 1 dia útil" required>

                    <button type="submit">Salvar Orçamento</button>
                </form>
                <a class="link-painel" href="/painel">📊 Ir para o Painel de Controle</a>
            </div>
        </body>
    </html>
    """

# 4. Rota para receber os dados e redirecionar para o painel
@app.post("/enviar-orcamento")
async def enviar_orcamento(
    nomeCliente: str = Form(...),
    whatsapp: str = Form(...),
    aparelho: str = Form(...),
    defeito: str = Form(...),
    precoEst: float = Form(...),
    tempoEst: str = Form(...)
):
    await prisma.orcamento.create(
        data={
            'nomeCliente': nomeCliente,
            'whatsapp': whatsapp,
            'aparelho': aparelho,
            'defeito': defeito,
            'precoEst': precoEst,
            'tempoEst': tempoEst
        }
    )
    # Após salvar, joga o usuário direto para o painel de visualização
    return RedirectResponse(url="/painel", status_code=303)

# 5. NOVA ROTA: O Painel de Controle que puxa os dados da Neon
@app.get("/painel", response_class=HTMLResponse)
async def painel():
    # Busca todos os orçamentos salvos na nuvem do mais novo para o mais antigo
    listagem = await prisma.orcamento.find_many(order={'createdAt': 'desc'})
    
    # Monta as linhas da tabela dinamicamente
    linhas_tabela = ""
    for os in listagem:
        linhas_tabela += f"""
        <tr>
            <td>{os.nomeCliente}</td>
            <td>{os.whatsapp}</td>
            <td>{os.aparelho}</td>
            <td>{os.defeito}</td>
            <td>R$ {os.precoEst:.2f}</td>
            <td>{os.tempoEst}</td>
            <td><span class="status-badge">{os.status}</span></td>
        </tr>
        """

    if not listagem:
        linhas_tabela = "<tr><td colspan='7' style='text-align:center; color:#888;'>Nenhum orçamento cadastrado ainda.</td></tr>"

    return f"""
    <html>
        <head>
            <title>Lange Reparos - Painel</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; }}
                .container {{ max-width: 1000px; background: white; padding: 20px; margin: 20px auto; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
                h2 {{ color: #333; display: flex; justify-content: space-between; align-items: center; }}
                .btn-novo {{ background-color: #007bff; color: white; padding: 10px 15px; text-decoration: none; border-radius: 4px; font-size: 14px; font-weight: bold; }}
                .btn-novo:hover {{ background-color: #0056b3; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #343a40; color: white; }}
                tr:hover {{ background-color: #f1f1f1; }}
                .status-badge {{ background-color: #ffc107; color: #212529; padding: 5px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>
                    <span>📊 Painel de Orçamentos - Lange Reparos</span>
                    <a class="btn-novo" href="/">+ Novo Orçamento</a>
                </h2>
                <table>
                    <thead>
                        <tr>
                            <th>Cliente</th>
                            <th>WhatsApp</th>
                            <th>Aparelho</th>
                            <th>Defeito</th>
                            <th>Preço</th>
                            <th>Tempo Est.</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {linhas_tabela}
                    </tbody>
                </table>
            </div>
        </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)