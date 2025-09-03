# Importar biblioteca
from openai import OpenAI
import streamlit as st
from rapidfuzz import fuzz
import os
from dotenv import load_dotenv


# Criar cliente da OpenAI
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

st.title("Assistente de Classificação de Exames")
st.markdown("Cole a requisição do paciente e selecione o exame:")

# Entrada de texto: apenas a requisição
requisicao = st.text_area("Requisição do paciente:")

# Checkbox para OpenAI (sempre disponível)
usar_openai_checkbox = st.checkbox("Deseja consultar o OpenAI para sugestão, mesmo que haja correspondência?")

# Seleção do exame
exame = st.selectbox(
    "Selecione o exame",
    [
        "Ultrassonografia de Abdômen Superior",
        "Ultrassonografia de Abdômen total",
        "Ultrassonografia de Mamas Bilateral",
        "Ultrassonografia de Próstata",
        "Ultrassonografia do Aparelho Urinário Adulto",
        "Ultrassonografia Pélvica Ginecológica",
        "Ultrassonografia do Aparelho Urinário (Rins, Bexiga) Pediátrico",
        "Ultrassonografia das Articulações",
        "Ultrassonografia da Tireoide",
        "Ultrassonografia Transvaginal",
        "Ultrassonografia de Bolsa Escrotal",
        "Ultrassonografia de Partes Moles"
    ]
)

# Prioridade das cores e mapeamento de cores
prioridade_cores = ["Vermelho", "Amarelo", "Verde", "Azul"]
cor_html = {"Vermelho": "red", "Amarelo": "orange", "Verde": "green", "Azul": "blue"}
  
criterios = {
    "Ultrassonografia de Abdômen Superior": {
        "Vermelho": ["lesões tumorais", "císticas", "sólidas"],
        "Amarelo": ["colelitíase sintomática", "investigação de hepatoesplenomegalia", "rastreamento de hepatocarcinoma"],
        "Verde": ["investigação de dor abdominal", "investigação de alterações laboratoriais hepáticas", "investigação de alterações laboratoriais pancreáticas"],
        "Azul": ["controle de lesões pancreáticas", "cistos", "nódulos", "pancreatite crônica", "controle de lesões hepáticas", "nódulos benignos", "esteatose hepática", "pólipos de vesícula biliar"]
    },
    "Ultrassonografia de Abdômen total":{
        "Vermelho": ["Lesões Tumorais ","Císticas e Sólidas", "aneurismas"],
        "Amarelo":["Dor abdominal atípica"],
        "Verde": ["Investigação de dor abdominal", "dor pélvica crônica"],
        "Azul": ["Acompanhamento de lesões benignas"]
    },
    "Ultrassonografia de Mamas Bilateral": {
        "Vermelho": ["mamografia BI-RADS IV", "V", "VI","descarga mamilar sem descrição de nódulos","seguimento de cá de mama","ginecomastia"],
        "Amarelo": ["mamografia BI-RADS 0", "III", "identificar e caracterizar anormalidades palpáveis", "massas palpáveis em mulheres com idade abaixo de 35 anos"],
        "Verde": ["história familiar de cá de mama sem descrição de nódulos","Mmg com mamas densas  birads 2","mastalgia sem sinais de alarme","paciente em TRH","uso de prótese mamária sem descrição de complicações nodulos"],
        "Azul": ["avaliar problemas associados com implantes mamários"]
    },
    "Ultrassonografia de Próstata": {
        "Vermelho": ["tumores", "controle de abscesso"],
        "Amarelo": ["prostatite", "prostatismo"],
        "Verde": ["PSA elevado"],
        "Azul": ["HPB", "infertilidade"]
    },
    "Ultrassonografia do Aparelho Urinário Adulto": {
        "Vermelho": ["suspeita de tumores", "insuficiência renal"],
        "Amarelo": ["controle de nódulos/ cistos renais complexos", "litíase sintomática", "suspeita de HAS renovascular"],
        "Verde": ["ITU de repetição", "malformação"],
        "Azul": ["disfunção miccional", "rim policístico"]
    },
    "Ultrassonografia Pélvica Ginecológica": {
        "Vermelho": ["dor pélvica aguda", "investigação de massa abdominal", "diagnóstico diferencial de tumores pélvicos"],
        "Amarelo": ["sangramento genital anormal no menacme", "pós-menopausa", "pós-inserção de DIU", "miomas uterinos volumosos"],
        "Verde": ["amenorreia primária", "amenorreia secundária não relacionada à gravidez"],
        "Azul": ["dor pélvica crônica", "tumores e cistos ovarianos pré e pós-menopausa"]
    },
    "Ultrassonografia do Aparelho Urinário (Rins, Bexiga) Pediátrico":{
        "Vermelho": ["Infecção urinária de repetição","massa abdominal","hematúria","diagnóstico pré-natal de hidronefrose","insuficiência renal","suspeita de hipertensão renovascular"],
        "Amarelo": ["Incontinência urinária", "hidronefrose unilateral", "Malformações do trato genito-urinário"],
        "Verde": ["Rim Policístico"],
        "Azul": ["Avaliação de cálculos urinários"]
    },
    "Ultrassonografia das Articulações":{
        "Vermelho": ["Artrite séptica"],
        "Amarelo": ["Derrames articulares", "doenças reumatológicas de base"],
        "Verde": [],
        "Azul": ["Tendinites", "cistos sinoviais", "lesão por esforço repetido", "bursites","espessamento de bainha tendinosa de qualquer natureza"]
    },
    "Ultrassonografia da Tireoide":{
        "Vermelho": ["Tumores", "nódulo suspeito de neoplasia"],
        "Amarelo": ["Hipotireoidismo", "hipertireoidismo"],
        "Verde": [ "Cisto"],
        "Azul": ["Bócio", "controle de nódulos Bethesda I, II e III"]
    },
    "Ultrassonografia Transvaginal":{
        "Vermelho": ["Dor pélvica aguda", "investigação de massa abdominal", "diagnóstico diferencial de tumores pélvicos", "gestação tubária"],
        "Amarelo": ["Sangramento genital anormal no menacme", "pós-menopausa", "pós-inserção de DIU", "gestação de 1º trimestre"],
        "Verde": ["Amenorreia primária", "amenorreia secundária não relacionada à gravidez"],
        "Azul":["Dor pélvica crônica", "tumores", "cistos ovarianos", "pré-menopausa", "pós-menopausa"]
    },
    "Ultrassonografia de Bolsa Escrotal":{
        "Vermelho": ["Tumores", "dor escrotal aguda"],
        "Amarelo": ["Controle de Infecções",  "torção de testículo"],
        "Verde": ["Aumento de volume da bolsa escrotal"],
        "Azul": ["Varicocele", "cistos de cordão"]
    },
    "Ultrassonografia de Partes Moles":{
        "Vermelho": [],
    }
    
}


# Prompt da médica reguladora
prompt_reguladora = """
Você é uma médica reguladora e precisa fazer a regulação de exames com base em protocolo pré-estabelecido.
Muitas descrições clínicas do caso não se enquadram perfeitamente nos critérios objetivos do protocolo. Portanto, utilize sua expertise como médica para analisar a solicitação considerando sinais e sintomas, exame físico e resultados de exames, mesmo que nem todos os critérios estejam claros. Seja criteriosa, mas objetiva. Baseie suas decisões em evidências médicas confiáveis sempre que necessário.

Retorne no seguinte formato:

situacao clinica: <descrição resumida da situação clínica>
raciocinio reguladora: <explicação do seu raciocínio médico e critérios utilizados>
classificacao final: <Vermelho, Amarelo, Verde , Azul e o motivo pela classificação final  >

Exemplo de resposta esperada:

Situacao clinica: Paciente com dor torácica súbita e falta de ar
raciocinio reguladora: Paciente apresenta sinais de alerta que podem indicar síndrome coronariana aguda. Necessário priorizar atendimento imediato conforme protocolos de urgência.
classificacao final: Vermelho 
"""

# Função de análise
def analisar_pedido(exame, indicacao, limiar=70):
    if exame not in criterios:
        return "<p style='font-size:18px'>Exame não encontrado nos critérios.</p>"

    correspondencias = []

    # Busca aproximada usando RapidFuzz
    for cor in prioridade_cores:
        for palavra in criterios[exame].get(cor, []):
            score = fuzz.partial_ratio(palavra.lower(), indicacao.lower())
            if score >= limiar:
                correspondencias.append((score, prioridade_cores.index(cor), cor, palavra))

    resultado_html = ""
    if correspondencias:
        # Ordena por similaridade decrescente, depois prioridade da cor
        correspondencias.sort(key=lambda x: (-x[0], x[1]))
        for score, _, cor, palavra in correspondencias:
            color = cor_html.get(cor, "black")
            resultado_html += f"<p style='font-size:20px; color:{color}'>Cor: {cor} | Palavra semelhante: '{palavra}' | Similaridade: {score:.0f}%</p>"
    else:
        resultado_html += "<p style='font-size:18px'>Nenhuma correspondência encontrada nos critérios.</p>"

    # Consulta OpenAI sempre disponível se checkbox marcado
    if usar_openai_checkbox:
        prompt = f"{prompt_reguladora}\nIndicação: '{indicacao}'\nExame: '{exame}'"
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é uma médica reguladora e precisa fazer a regulação de exames com base em protocolo pré-estabelecido. Porém muitas descrições clínicas do caso não se enquadram corretamente nos critérios objetivos do protocolo. Então você precisa utilizar sua expertise como médica e analisar a solicitação com base nos dados clínicos ofertados que podem ter sinais e sintomas, exame físico e até mesmo resultado de exames. Você precisa ser criteriosa mas ao mesmo tempo objetiva. Se necessário, busque dados confiáveis embasadas na medicina baseada em evidências.sugira a categoria (Vermelho, Amarelo, Verde ou Azul) e dê uma breve justificativa.Retorne no formato.Cor: <cor> Justificativa: <explicação>"},
                {"role": "user", "content": prompt}
            ]
        )
        # Recebe a resposta
        resposta_texto = resposta.choices[0].message.content.strip()

        # Formata para quebrar linhas depois de cada campo
        resposta_formatada = resposta_texto.replace("Situação clinica:", "Situação clinica:\n") \
                                        .replace("Raciocinio reguladora:", "\nRaciocinio reguladora:\n") \
                                        .replace("Classificação final:", "\nClassificação final:\n")

        # Exibe no Streamlit
        resultado_html += f"<p style='font-size:18px; color:black; font-weight:bold'>Consulta OpenAI:<br>{resposta_formatada}</p>"


    return resultado_html

# Botão de execução
if st.button("Analisar requisição"):
    if requisicao.strip() == "":
        st.error("Cole a requisição do paciente antes de analisar.")
    else:
        resultado = analisar_pedido(exame, requisicao)
        st.markdown(resultado, unsafe_allow_html=True)