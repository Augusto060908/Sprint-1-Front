import streamlit as st
import pandas as pd
import numpy as np
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FORZY - Gestão de Ativos", layout="wide")

# --- DICIONÁRIO DE MOCKS (Rastreabilidade e Integração) ---
# Estrutura JSON/Dict documentada para mapeamento "de-para"
mock_hierarquia = {
    "Planta São Paulo (Matriz)": {
        "Área de Moagem": ["MOT-001 (Moinho Principal)", "MOT-002 (Moinho Secundário)"],
        "Área de Envase": ["MOT-003 (Esteira A)"]
    },
    "Planta Rio de Janeiro": {
        "Área de Compressão": ["COMP-101 (Compressor de Ar)", "COMP-102 (Reserva)"]
    }
}

def init_state():
    if 'equipamentos' not in st.session_state:
        st.session_state['equipamentos'] = pd.DataFrame(
            columns=['TAG', 'Fabricante', 'Modelo', 'Potência (W)', 'Tensão (V)']
        )

def avaliar_saude_sensor(valor, limite_amarelo, limite_vermelho, unidade, nome_sensor):
    """Gera cor semântica e a justificativa textual (Explainability)."""
    if valor >= limite_vermelho:
        cor = "red"
        status = "CRÍTICO"
        msg = f"O valor atual ({valor:.1f} {unidade}) excede o limite operacional crítico de {limite_vermelho} {unidade}."
    elif valor >= limite_amarelo:
        cor = "orange"
        status = "ALERTA"
        msg = f"O valor atual ({valor:.1f} {unidade}) atingiu o limite de alerta preventivo ({limite_amarelo} {unidade})."
    else:
        cor = "green"
        status = "NORMAL"
        msg = f"Operação normal. {nome_sensor} operando dentro dos limites de segurança estabelecidos."
    
    return cor, status, msg

# --- TELAS ---

def view_monitoramento_hierarquico(perfil):
    st.header("🏭 Monitoramento Operacional de Ativos")
    
    # 1. Transparência sobre a Natureza dos Dados (Governança)
    st.warning("⚠️ **Transparência de Dados:** As informações apresentadas nesta tela são originadas de fontes estáticas (Mocks/JSON) para fins de teste de interface e homologação, não representando telemetria em tempo real.")

    # 2. RBAC - Controle de Exibição de Plantas
    plantas_disponiveis = list(mock_hierarquia.keys())
    
    st.subheader("Filtros de Localização")
    if perfil == "Técnico Regional (SP)":
        plantas_disponiveis = ["Planta São Paulo (Matriz)"]
        st.info("🔒 **Acesso Restrito Aplicado:** Seu perfil permite visualização apenas para a unidade de São Paulo.")

    col1, col2 = st.columns(2)
    with col1:
        planta = st.selectbox("Selecione a Planta", plantas_disponiveis)
    with col2:
        area = st.selectbox("Selecione a Área", list(mock_hierarquia[planta].keys()))
        
    equipamento = st.selectbox("Selecione o Equipamento Ativo", mock_hierarquia[planta][area])

    st.markdown("---")
    
    # 3. Rastreabilidade da Navegação (Breadcrumbs)
    st.caption(f"📍 **Rastreabilidade Hierárquica (Linhagem):** {planta} > {area} > {equipamento}")
    
    st.subheader(f"Telemetria em Tempo Real: {equipamento}")
    
    # Simulando dados
    temp_atual = np.random.uniform(60, 95)
    vibracao_atual = np.random.uniform(2.0, 8.0)
    
    # 4. Explicabilidade (Explainability) e Status Semântico
    c_temp, s_temp, m_temp = avaliar_saude_sensor(temp_atual, 75.0, 85.0, "°C", "Temperatura")
    c_vib, s_vib, m_vib = avaliar_saude_sensor(vibracao_atual, 5.0, 7.0, "mm/s", "Vibração")
    
    col_sensor1, col_sensor2 = st.columns(2)
    
    with col_sensor1:
        st.markdown(f"### 🌡️ Temperatura: :{c_temp}[{temp_atual:.1f} °C]")
        st.markdown(f"**Status:** :{c_temp}[{s_temp}]")
        st.info(f"**Justificativa (IA):** {m_temp}")
        
    with col_sensor2:
        st.markdown(f"### 📉 Vibração: :{c_vib}[{vibracao_atual:.1f} mm/s]")
        st.markdown(f"**Status:** :{c_vib}[{s_vib}]")
        st.info(f"**Justificativa (IA):** {m_vib}")

def view_consulta():
    st.header("📋 Consulta de Equipamentos Cadastrados")
    df = st.session_state['equipamentos']
    if df.empty:
        st.info("Nenhum equipamento cadastrado ainda.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

def view_cadastro():
    st.header("➕ Cadastro Técnico do Ativo")
    with st.form("form_cadastro", clear_on_submit=True):
        tag = st.text_input("TAG de Identificação *", placeholder="Ex: MOT-001")
        fabricante = st.text_input("Fabricante *", placeholder="Ex: WEG")
        potencia = st.number_input("Potência Nominal (W)", min_value=0.0, step=100.0)
        tensao = st.selectbox("Tensão de Alimentação (V)", ["220", "380", "440"])
        submit = st.form_submit_button("Cadastrar", type="primary")

        if submit:
            if tag and fabricante:
                novo = pd.DataFrame([{'TAG': tag.upper(), 'Fabricante': fabricante, 'Potência (W)': potencia, 'Tensão (V)': tensao}])
                st.session_state['equipamentos'] = pd.concat([st.session_state['equipamentos'], novo], ignore_index=True)
                st.success(f"Equipamento {tag.upper()} cadastrado!")
            else:
                st.error("Preencha TAG e Fabricante.")

def view_dados_brutos():
    st.header("📈 Visualização de Dados Brutos (Telemetria Avançada)")
    st.warning("Painel restrito para Engenharia de Confiabilidade.")
    df = st.session_state['equipamentos']
    if df.empty:
        st.warning("Cadastre um equipamento primeiro.")
        return
    tag_selecionada = st.selectbox("Selecione o Equipamento", df['TAG'].tolist())
    if st.button("Coletar Sinais", type="primary"):
        with st.spinner("Coletando..."):
            time.sleep(1)
            dados = pd.DataFrame({
                'Tempo (s)': range(1, 21),
                'Tensão (V)': np.random.normal(220, 2, 20),
                'Corrente (A)': np.random.normal(10, 0.5, 20)
            })
            st.line_chart(dados.set_index('Tempo (s)'))
            st.dataframe(dados, use_container_width=True)

# --- MENU E RBAC PRINCIPAL ---
def main():
    init_state()
    
    st.sidebar.title("⚙️ FORZY App")
    
    # Módulo de RBAC
    st.sidebar.markdown("---")
    st.sidebar.subheader("👤 Simulador de Perfil (RBAC)")
    perfil = st.sidebar.selectbox("Selecione o seu cargo:", [
        "Gestor Global / Admin", 
        "Técnico Regional (SP)", 
        "Operador de Linha"
    ])
    st.sidebar.markdown("---")
    
    # Navegação Dinâmica
    opcoes_menu = ["Monitoramento Operacional", "Consulta de Equipamentos", "Cadastro Técnico"]
    
    # Regra RBAC: Operador de Linha NÃO tem acesso aos Dados Brutos Sensíveis
    if perfil != "Operador de Linha":
        opcoes_menu.append("Dados Brutos (Engenharia)")
    
    menu = st.sidebar.radio("Navegação", opcoes_menu)
    st.sidebar.markdown("---")
    st.sidebar.caption("Sprint 3 - Gov & Front-End")

    # Roteamento
    if menu == "Monitoramento Operacional":
        view_monitoramento_hierarquico(perfil)
    elif menu == "Consulta de Equipamentos":
        view_consulta()
    elif menu == "Cadastro Técnico":
        view_cadastro()
    elif menu == "Dados Brutos (Engenharia)":
        view_dados_brutos()

if __name__ == "__main__":
    main()
