# Assistente-ultrassom

# Assistente de Classificação de Exames

Este projeto usa Streamlit e OpenAI para sugerir categorias de exames com base em critérios pré-definidos.

## Como rodar localmente

1. Clone o repositório:
```bash
git clone https://github.com/seuusuario/assistente-ultrassom.git

##Entre na pasta:

cd assistente-ultrassom


##Crie e ative o ambiente virtual (opcional mas recomendado):

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate


##Instale as dependências:

pip install -r requirements.txt


##Crie a pasta .streamlit e o arquivo secrets.toml:

[openai]
api_key = "SUA_CHAVE_OPENAI"


##Rode o projeto:

streamlit run assistente_exames.py


Abra o link que aparecer no terminal (geralmente http://localhost:8501) no navegador.


---

## 3️⃣ Verificar se tudo está pronto

- `.gitignore` está configurado ✅  
- `requirements.txt` com todas as libs ✅  
- Código usa `st.secrets` para a API ✅  
- `README.md` explicativo ✅  
