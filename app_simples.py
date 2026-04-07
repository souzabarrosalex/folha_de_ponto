import streamlit as st
from db_simples import conectar, criar_tabelas
import datetime

dados_existentes = None


def limpar_campos():
    manter = ["tipo", "mes", "ano"]

    for key in list(st.session_state.keys()):
        if key not in manter:
            del st.session_state[key]


criar_tabelas()

st.title("📄 Folha Simples")


# 🔥 AQUI
st.markdown("""
<style>
.bloco {
    font-family: Arial, sans-serif;
    font-size: 16px;
    line-height: 1.8;
}
.titulo-bloco {
    font-size: 22px;
    font-weight: bold;
    margin-top: 20px;
}
.linha {
    display: flex;
    justify-content: space-between;
    border-bottom: 1px solid #ddd;
    padding: 4px 0;
}
.label {
    font-weight: 500;
}
.valor {
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


tipo = st.selectbox("Tipo de folha", ["Adiantamento", "Fechamento"], key="tipo")
mes = st.selectbox("Mês", list(range(1, 13)), key="mes")
ano = st.selectbox("Ano", [2026], key="ano")

conn = conectar()
cursor = conn.cursor()

cursor.execute("""
SELECT *
FROM fechamento
WHERE mes = ? AND ano = ? AND tipo = ?
ORDER BY id DESC
""", (mes, ano, tipo))

dados_lista = cursor.fetchall()

colunas = [desc[0] for desc in cursor.description]

conn.close()

import pandas as pd

if dados_lista:
    df = pd.DataFrame(dados_lista, columns=colunas)
    st.dataframe(df, use_container_width=True)
else:
    st.info("Nenhum lançamento encontrado para esse período")

import pandas as pd

# 🔥 TABELA NO TOPO (USANDO MES E ANO SELECIONADOS)
st.markdown("---")
st.subheader("📋 Lançamentos do período")

conn = conectar()
cursor = conn.cursor()


# ---------------- FUNCIONÁRIO ----------------
st.subheader("👤 Funcionário")

conn = conectar()
cursor = conn.cursor()

cursor.execute("SELECT nome FROM funcionarios ORDER BY nome ASC")
dados = [r[0] for r in cursor.fetchall()]

opcoes_func = ["Selecione..."] + dados + ["➕ Novo"]

nome = st.selectbox("Funcionário", opcoes_func, index=0, key="funcionario_select")

if nome == "Selecione...":
    nome = None

    conn.close()

elif nome == "➕ Novo":
    novo_nome = st.text_input("Nome do Funcionário", key="novo_funcionario")

    if st.button("Salvar Funcionário", key="btn_salvar_funcionario"):
        if novo_nome.strip() == "":
            st.error("Digite o nome")
        else:
            cursor.execute("INSERT INTO funcionarios (nome) VALUES (?)", (novo_nome,))
            conn.commit()

            st.success("Funcionário cadastrado!")

            # 🔥 NÃO mexe no session_state aqui
            st.rerun()

    cursor.execute("""
    SELECT *
    FROM fechamento
    WHERE funcionario = ?
    AND tipo = ?
    AND mes = ?
    AND ano = ?
    LIMIT 1
    """, (nome, tipo, mes, ano))

    dados = cursor.fetchall()
    conn.commit()
    conn.close()



# ---------------- CADASTROS AUXILIARES ----------------
def campo_com_cadastro(label, tabela, key_base, valor_padrao=None):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(f"SELECT nome FROM {tabela} ORDER BY nome ASC")
    dados = [r[0] for r in cursor.fetchall()]
    # 🔥 GARANTE QUE O VALOR EXISTE
    if valor_padrao and valor_padrao not in dados:
        dados.append(valor_padrao)
    conn.close()

    opcoes = ["Selecione..."] + dados + ["➕ Novo"]

    # 🔥 define índice baseado no valor do banco
    if valor_padrao and valor_padrao in dados:
        index = opcoes.index(valor_padrao)
    else:
        index = 0

    key = f"{key_base}_select"

    # 🔥 se já tem valor no session_state, usa ele
    if key in st.session_state and st.session_state[key] in opcoes:
        index = opcoes.index(st.session_state[key])
    else:
        index = 0

    valor = st.selectbox(label, opcoes, key=key)

    if valor == "➕ Novo":
        st.session_state[f"{key_base}_novo_ativo"] = True

    if st.session_state.get(f"{key_base}_novo_ativo", False):

        novo = st.text_input(f"Novo {label}", key=f"{key_base}_novo")

        if st.button(f"Salvar {label}", key=f"{key_base}_btn"):

            if novo.strip() == "":
                st.error("Digite um valor")
            else:
                conn = conectar()
                cursor = conn.cursor()

                cursor.execute(f"INSERT INTO {tabela} (nome) VALUES (?)", (novo,))
                conn.commit()
                conn.close()

                st.success(f"{label} cadastrado!")

                st.session_state[f"{key_base}_novo_ativo"] = False
                st.rerun()

        return novo

    if valor == "Selecione...":
        return None

    return valor


if nome:

    if nome:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT 
        funcionario,
        empresa,
        setor,
        cargo,
        obra,
        cidade,
        tipo,
        ano,
        mes,
        salario,
        premio,
        filhos,
        desconto,
        dias_normais,
        dias_faltas,
        dsr,
        horas_falta,
        valor_dias_normais,
        valor_premio,
        salario_familia,
        dias_faltas_valor,
        dsr_faltas_valor,
        horas_faltas_valor,
        base_inss,
        inss,
        total_vencimentos,
        total_descontos,
        liquido
        FROM fechamento
        WHERE funcionario = ?
        AND tipo = ?
        AND mes = ?
        AND ano = ?
        LIMIT 1
        """, (nome, tipo, mes, ano))

        dados_existentes = cursor.fetchone()
        conn.close()   

        colunas = [desc[0] for desc in cursor.description]

if dados_existentes:
    dados_existentes = dict(zip(colunas, dados_existentes))


if dados_existentes:
    st.session_state["empresa_select"] = dados_existentes["empresa"]
    st.session_state["setor_select"] = dados_existentes["setor"]
    st.session_state["cargo_select"] = dados_existentes["cargo"]
    st.session_state["obra_select"] = dados_existentes["obra"]
    st.session_state["cidade_select"] = dados_existentes["cidade"]

    
if nome:
    empresa = campo_com_cadastro("Empresa", "empresas", "empresa", dados_existentes["empresa"] if dados_existentes else None)
    setor = campo_com_cadastro("Setor", "setores", "setor", dados_existentes["setor"] if dados_existentes else None)
    cargo = campo_com_cadastro("Cargo", "cargos", "cargo", dados_existentes["cargo"] if dados_existentes else None)
    obra = campo_com_cadastro("Obra", "obras", "obra", dados_existentes["obra"] if dados_existentes else None)
    cidade = campo_com_cadastro("Cidade", "cidades", "cidade", dados_existentes["cidade"] if dados_existentes else None)


# ---------------- CAMPOS ----------------
if nome:

    conn.close()

    salario = st.number_input(
        "Salário",
        min_value=0.0,
        value=dados_existentes["salario"] if dados_existentes else 0.0,
        key="salario"
    )

    premio = st.number_input(
        "Prêmio",
        min_value=0.0,
        value=dados_existentes["premio"] if dados_existentes else 0.0,
        key="premio"
    )

    dias_normais = st.number_input(
        "Dias Normais",
        value=dados_existentes["dias_normais"] if dados_existentes else 0
    )

    dias_faltas = st.number_input(
        "Dias Faltas",
        value=dados_existentes["dias_faltas"] if dados_existentes else 0
    )

    dsr = st.number_input(
        "DSR",
        value=dados_existentes["dsr"] if dados_existentes else 0
    )

    # hora precisa converter
    hora_padrao = datetime.time(0, 0)

    if dados_existentes and dados_existentes["horas_falta"]:
        try:
            h, m = map(int, dados_existentes[5].split(":")[:2])
            hora_padrao = datetime.time(h, m)
        except:
            pass

    horas_falta = st.time_input(
        "Horas Faltas Parciais",
        value=hora_padrao,
        key="horas_falta"
    )


    filhos = st.number_input(
    "Quantidade de filhos",
    min_value=0,
    value=dados_existentes["filhos"] if dados_existentes else 0,
    key="filhos"
)
    horas_faltas_decimal = horas_falta.hour + (horas_falta.minute / 60)
    desconto = st.number_input(
    "Desconto Salarial",
    min_value=0.0,
    value=dados_existentes["desconto"] if dados_existentes else 0.0,
    key="desconto"
)

    # ---------------- DÍVIDA ----------------
    tipo_divida = st.selectbox("Tipo", ["Nenhum", "Empréstimo", "Dívida"], key="tipo_divida")

    parcela = ""
    valor_divida = 0
    descricao = ""

    if tipo_divida == "Empréstimo":
        parcela = st.text_input("Parcela (ex: 1/10)", key="parcela")
        valor_divida = st.number_input("Valor da parcela", min_value=0.0, key="valor_parcela")
        descricao = st.text_input("Descrição", key="desc_emprestimo")

    elif tipo_divida == "Dívida":
        valor_divida = st.number_input("Valor da dívida", min_value=0.0, key="valor_divida")
        descricao = st.text_input("Descrição", key="desc_divida")

    # ---------------- VALIDAÇÃO ----------------
    confirmar = False
    if filhos == 0:
        confirmar = st.checkbox("Confirmo que não possui filhos", key="confirmar_filhos")



    def calcular_inss(base):
        inss = 0

        faixas = [
            (1518.00, 0.075),
            (2793.88, 0.09),
            (4190.83, 0.12),
            (8157.41, 0.14),
        ]

        anterior = 0

        for limite, aliquota in faixas:
            if base > limite:
                inss += (limite - anterior) * aliquota
                anterior = limite
            else:
                inss += (base - anterior) * aliquota
                return round(inss, 2)

        # teto
        return round(inss, 2)   
    
    def calcular_folha():
        valor_dias_normais = (salario / 30) * dias_normais
        valor_premio = (premio / 30) * dias_normais
        salario_familia = (67.54 / 30) * dias_normais * filhos

        horas_faltas_decimal = horas_falta.hour + (horas_falta.minute / 60)

        dias_faltas_valor = ((salario + premio) / 30) * dias_faltas
        dsr_faltas_valor = ((salario + premio) / 30) * dsr
        horas_faltas_valor = ((salario + premio) / 220) * horas_faltas_decimal

        base_inss = valor_dias_normais - dias_faltas_valor - dsr_faltas_valor - horas_faltas_valor

        if base_inss < 0:
            base_inss = 0

        inss_valor = calcular_inss(base_inss)

        total_vencimentos = valor_dias_normais + valor_premio + salario_familia

        total_descontos = (
            dias_faltas_valor +
            dsr_faltas_valor +
            horas_faltas_valor +
            inss_valor
        )

        valor_liquido = total_vencimentos - total_descontos

        return {
            "valor_dias_normais": valor_dias_normais,
            "valor_premio": valor_premio,
            "salario_familia": salario_familia,
            "dias_faltas_valor": dias_faltas_valor,
            "dsr_faltas_valor": dsr_faltas_valor,
            "horas_faltas_valor": horas_faltas_valor,
            "base_inss": base_inss,
            "inss_valor": inss_valor,
            "total_vencimentos": total_vencimentos,
            "total_descontos": total_descontos,
            "valor_liquido": valor_liquido
        }

    
    simular = st.button("🧮 Simular Fechamento") 


    if simular:
        
        # 🔹 Cálculos
        valor_dias_normais = (salario / 30) * dias_normais
        valor_premio = (premio / 30) * dias_normais
        salario_familia = (67.54 / 30) * dias_normais * filhos

        # 🔹 Exibição
        st.markdown(f"""
            <div class="bloco">

            <div class="titulo-bloco">🟩 Vencimentos</div>

            <div class="linha">
                <div class="label">Valor Dias Normais</div>
                <div class="valor">R$ {valor_dias_normais:.2f}</div>
            </div>

            <div class="linha">
                <div class="label">Prêmio de Eficiência</div>
                <div class="valor">R$ {valor_premio:.2f}</div>
            </div>

            <div class="linha">
                <div class="label">Salário Família</div>
                <div class="valor">R$ {salario_familia:.2f}</div>
            </div>

            </div>
            """, unsafe_allow_html=True)
        

  


    if simular:



        # 🔹 Conversão de horas
        horas_faltas_decimal = horas_falta.hour + (horas_falta.minute / 60)

        # 🔹 Cálculos
        dias_faltas_valor = ((salario + premio) / 30) * dias_faltas
        dsr_faltas_valor = ((salario + premio) / 30) * dsr
        horas_faltas_valor = ((salario + premio) / 220) * horas_faltas_decimal
        

        # 🔹 Exibição
        st.markdown(f"""
            <div class="bloco">

            <div class="titulo-bloco">🟥 Descontos</div>

            <div class="linha">
                <div class="label">Dias Faltas</div>
                <div class="valor">R$ {dias_faltas_valor:.2f}</div>
            </div>

            <div class="linha">
                <div class="label">DSR Faltas</div>
                <div class="valor">R$ {dsr_faltas_valor:.2f}</div>
            </div>

            <div class="linha">
                <div class="label">Horas Faltas Parciais</div>
                <div class="valor">R$ {horas_faltas_valor:.2f}</div>
            </div>

            <!-- 🔥 AQUI -->
            <div class="linha">
                <div class="label">Desconto Salarial</div>
                <div class="valor">R$ {desconto:.2f}</div>
            </div>

            </div>
        """, unsafe_allow_html=True)


        base_inss = valor_dias_normais - dias_faltas_valor - dsr_faltas_valor - horas_faltas_valor

        # não pode ser negativa
        if base_inss < 0:
            base_inss = 0

        inss_valor = calcular_inss(base_inss)


        st.markdown(f"""
        <div class="bloco">

        <div class="titulo-bloco">🧾 INSS</div>

        <div class="linha">
            <div class="label">Base INSS</div>
            <div class="valor">R$ {base_inss:.2f}</div>
        </div>

        <div class="linha">
            <div class="label">Desconto INSS</div>
            <div class="valor">R$ {inss_valor:.2f}</div>
        </div>

        </div>
        """, unsafe_allow_html=True)


        # 🔹 Totais
        total_vencimentos = valor_dias_normais + valor_premio + salario_familia

        total_descontos = (
            dias_faltas_valor +
            dsr_faltas_valor +
            horas_faltas_valor +
            inss_valor +
            desconto
        )

        valor_liquido = total_vencimentos - total_descontos



        st.markdown("## 🟦 Resumo da Folha")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.success(f"💰 Vencimentos\nR$ {total_vencimentos:.2f}")

        with col2:
            st.error(f"📉 Descontos\nR$ {total_descontos:.2f}")

        with col3:
            st.info(f"💵 Líquido\nR$ {valor_liquido:.2f}")



    # ---------------- SALVAR ----------------


    if st.button("💾 Salvar Fechamento", key="btn_salvar"):

        if filhos == 0 and not confirmar:
            st.error("Confirme que o funcionário não possui filhos")
            st.stop()

        resultado = calcular_folha()

        dados = {
            "funcionario": nome,
            "empresa": empresa,
            "setor": setor,
            "cargo": cargo,
            "obra": obra,
            "cidade": cidade,

            "tipo": tipo,
            "ano": ano,
            "mes": mes,

            "salario": salario,
            "premio": premio,

            "filhos": filhos,
            "desconto": desconto,

            "dias_normais": dias_normais,
            "dias_faltas": dias_faltas,
            "dsr": dsr,
            "horas_falta": str(horas_falta),

            "valor_dias_normais": resultado["valor_dias_normais"],
            "valor_premio": resultado["valor_premio"],
            "salario_familia": resultado["salario_familia"],

            "dias_faltas_valor": resultado["dias_faltas_valor"],
            "dsr_faltas_valor": resultado["dsr_faltas_valor"],
            "horas_faltas_valor": resultado["horas_faltas_valor"],

            "base_inss": resultado["base_inss"],
            "inss": resultado["inss_valor"],

            "total_vencimentos": resultado["total_vencimentos"],
            "total_descontos": resultado["total_descontos"],
            "liquido": resultado["valor_liquido"]
        }

        conn = conectar()
        cursor = conn.cursor()

        colunas = ", ".join(dados.keys())
        placeholders = ", ".join(["?"] * len(dados))
        valores = list(dados.values())

        sql = f"""
        INSERT INTO fechamento ({colunas})
        VALUES ({placeholders})
        """

        cursor.execute(sql, valores)

        conn.commit()
        conn.close()
        st.success("Fechamento salvo com sucesso!")

        limpar_campos()

        st.rerun()

 

conn.close()





