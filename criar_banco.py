import asyncio
from prisma import Prisma

async def main():
    # Sua nova URL da Neon com a senha limpa
    db = Prisma(datasource={
        'url': 'postgresql://neondb_owner:npg_MFJYGyhju41W@ep-still-mouse-acd1nsal-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
    })
    
    print("🔄 Conectando à Neon...")
    try:
        await db.connect()
        
        # Cria a tabela no formato padrão PostgreSQL
        await db.execute_raw('''
            CREATE TABLE IF NOT EXISTS "Orcamento" (
                "id" TEXT PRIMARY KEY,
                "nomeCliente" TEXT NOT NULL,
                "whatsapp" TEXT NOT NULL,
                "aparelho" TEXT NOT NULL,
                "defeito" TEXT NOT NULL,
                "precoEst" DOUBLE PRECISION NOT NULL,
                "tempoEst" TEXT NOT NULL,
                "status" TEXT NOT NULL DEFAULT 'Pendente',
                "createdAt" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        print("✅ Tabela Orcamento verificada/criada com sucesso!")
    except Exception as e:
        print(f"❌ Erro na execução: {e}")
    finally:
        if db.is_connected():
            await db.disconnect()

if __name__ == '__main__':
    asyncio.run(main())