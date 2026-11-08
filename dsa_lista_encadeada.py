# -*- coding: utf-8 -*-
"""
Disciplina: Data Structures and Algorithms (DSA) — Global Solution 2026.2 (Citizen Tech)
Projeto: Citizen Assist AI — Central do Cidadao de Aurora

Implementacao de um sistema CRUD completo de catalogo de servicos publicos estruturado
exclusivamente sobre uma Lista Simplesmente Encadeada propria (NoServico e ListaEncadeadaServicos),
sem utilizacao de listas nativas do Python (list / []) para o armazenamento da colecao.

Inclui:
- Classe RegistroServico (modelo de dominio dos servicos da Central de Aurora)
- Classe NoServico (no de encadeamento explicito via referencia 'proximo')
- Classe ListaEncadeadaServicos (inserir, consultar_por_id, listar_todos, atualizar,
  excluir, pesquisar_por_atributo com Busca Sequencial normalizada e ordenar com
  Merge Sort in-place em ponteiros O(n log n))
- Bateria automatizada de testes e evidencias (incluindo operacoes em lista vazia)
- Interface de menu interativo resiliente a entradas invalidas
"""

from __future__ import annotations
import sys
from typing import Callable, Iterator, Optional, Tuple


MAPA_ACENTOS = str.maketrans(
    "áàâãäéèêëíìîïóòôõöúùûüçñÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑ",
    "aaaaaeeeeiiiiooooouuuucnAAAAAEEEEIIIIOOOOOUUUUCN",
)


def normalizar_texto(texto: str) -> str:
    """Normaliza uma string convertendo para minusculas, removendo acentos e espacos extras."""
    if not isinstance(texto, str):
        return ""
    limpo = texto.translate(MAPA_ACENTOS).lower().strip()
    for char in "?!.,;:()[]{}'\"/-":
        limpo = limpo.replace(char, " ")
    return " ".join(limpo.split())


class RegistroServico:
    """
    Representa um servico publico ou orientacao cadastrada na Central do Cidadao de Aurora.

    Atributos obrigatorios:
        id (int): Identificador unico positivo do servico.
        titulo (str): Nome ou titulo oficial do servico.
        categoria (str): Categoria tematica (ex.: Documentos, Trabalho e Mobilidade, etc.).
        descricao (str): Resumo das regras, prazos, taxas e documentos exigidos.
        publico_alvo (str): Quem pode solicitar o servico e regras de idade/representacao.
        canal_atendimento (str): Local presencial ou portal digital de atendimento.
    """

    def __init__(
        self,
        id: int,
        titulo: str,
        categoria: str,
        descricao: str,
        publico_alvo: str,
        canal_atendimento: str,
    ) -> None:
        self.id: int = id
        self.titulo: str = titulo.strip() if isinstance(titulo, str) else ""
        self.categoria: str = categoria.strip() if isinstance(categoria, str) else ""
        self.descricao: str = descricao.strip() if isinstance(descricao, str) else ""
        self.publico_alvo: str = publico_alvo.strip() if isinstance(publico_alvo, str) else ""
        self.canal_atendimento: str = (
            canal_atendimento.strip() if isinstance(canal_atendimento, str) else ""
        )

    def validar_campos(self) -> Tuple[bool, str]:
        """Valida se o ID e um inteiro positivo e se todos os campos textuais estao preenchidos."""
        if not isinstance(self.id, int) or isinstance(self.id, bool) or self.id <= 0:
            return False, "O campo 'id' deve ser um numero inteiro positivo maior que zero."
        if not self.titulo:
            return False, "O campo obrigatorio 'titulo' nao pode ser vazio."
        if not self.categoria:
            return False, "O campo obrigatorio 'categoria' nao pode ser vazio."
        if not self.descricao:
            return False, "O campo obrigatorio 'descricao' nao pode ser vazio."
        if not self.publico_alvo:
            return False, "O campo obrigatorio 'publico_alvo' nao pode ser vazio."
        if not self.canal_atendimento:
            return False, "O campo obrigatorio 'canal_atendimento' nao pode ser vazio."
        return True, "Registro valido."

    def copiar(self) -> RegistroServico:
        """Retorna uma copia independente do registro de servico."""
        return RegistroServico(
            id=self.id,
            titulo=self.titulo,
            categoria=self.categoria,
            descricao=self.descricao,
            publico_alvo=self.publico_alvo,
            canal_atendimento=self.canal_atendimento,
        )

    def exibir_resumo(self) -> str:
        """Formata o registro em linha unica para listagens tabulares."""
        return (
            f"[ID {self.id:02d}] {self.titulo} | "
            f"Categoria: {self.categoria} | Canal: {self.canal_atendimento}"
        )

    def exibir_detalhado(self) -> str:
        """Formata todos os atributos do registro para visualizacao completa no terminal."""
        linhas = (
            f"  ID do Servico     : {self.id}\n"
            f"  Titulo            : {self.titulo}\n"
            f"  Categoria         : {self.categoria}\n"
            f"  Descricao         : {self.descricao}\n"
            f"  Publico-Alvo      : {self.publico_alvo}\n"
            f"  Canal Atendimento : {self.canal_atendimento}"
        )
        return linhas

    def __str__(self) -> str:
        return self.exibir_resumo()

    def __repr__(self) -> str:
        return (
            f"RegistroServico(id={self.id}, titulo={self.titulo!r}, "
            f"categoria={self.categoria!r})"
        )


class NoServico:
    """
    Elemento fundamental (no) da Lista Simplesmente Encadeada.
    Armazena a carga util (dado: RegistroServico) e a referencia explicita para o proximo no.
    """

    def __init__(
        self, dado: RegistroServico, proximo: Optional[NoServico] = None
    ) -> None:
        self.dado: RegistroServico = dado
        self.proximo: Optional[NoServico] = proximo

    def __repr__(self) -> str:
        prox_id = self.proximo.dado.id if self.proximo is not None else None
        return f"NoServico(id={self.dado.id}, proximo_id={prox_id})"


class ListaEncadeadaServicos:
    """
    Estrutura de dados linear dinamica baseada em nos encadeados por ponteiros (NoServico).
    Nao utiliza listas nativas do Python (list / []) para armazenar ou ordenar os elementos.
    """

    def __init__(self) -> None:
        self.cabeca: Optional[NoServico] = None
        self.tamanho: int = 0
        self.ultima_mensagem: str = ""

    def esta_vazia(self) -> bool:
        """Retorna True se a lista encadeada nao possuir nenhum no."""
        return self.cabeca is None

    def __len__(self) -> int:
        return self.tamanho

    def __bool__(self) -> bool:
        return self.cabeca is not None

    def __iter__(self) -> Iterator[RegistroServico]:
        """Iterador que percorre os ponteiros 'proximo' em O(1) de memoria auxiliar."""
        atual = self.cabeca
        while atual is not None:
            yield atual.dado
            atual = atual.proximo

    def inserir(self, registro: RegistroServico, silencioso: bool = False) -> bool:
        """
        Insere um novo RegistroServico ao final da lista encadeada.
        Complexidade:
            - Melhor caso: O(1) quando a lista esta vazia (cabeca is None).
            - Caso medio e pior caso: O(n), pois percorre os n nos existentes para
              garantir unicidade do 'id' e localizar o ultimo no (cauda).
            - Espaco auxiliar: O(1).
        """
        if not isinstance(registro, RegistroServico):
            self.ultima_mensagem = "Erro: O objeto informado nao e uma instancia de RegistroServico."
            if not silencioso:
                print(f"  [!] {self.ultima_mensagem}")
            return False

        valido, msg_validacao = registro.validar_campos()
        if not valido:
            self.ultima_mensagem = f"Erro de validacao: {msg_validacao}"
            if not silencioso:
                print(f"  [!] {self.ultima_mensagem}")
            return False

        novo_no = NoServico(registro)

        # Caso 1: Lista vazia -> insercao imediata na cabeca em O(1)
        if self.cabeca is None:
            self.cabeca = novo_no
            self.tamanho = 1
            self.ultima_mensagem = f"Servico ID {registro.id} ('{registro.titulo}') inserido na cabeca da lista."
            return True

        # Caso 2: Travessia de ponteiros para verificar duplicidade de ID e encontrar o ultimo no
        atual = self.cabeca
        while True:
            if atual.dado.id == registro.id:
                self.ultima_mensagem = (
                    f"Erro: Ja existe um servico cadastrado com o ID {registro.id} "
                    f"('{atual.dado.titulo}'). Insercao rejeitada."
                )
                if not silencioso:
                    print(f"  [!] {self.ultima_mensagem}")
                return False
            if atual.proximo is None:
                break
            atual = atual.proximo

        atual.proximo = novo_no
        self.tamanho += 1
        self.ultima_mensagem = f"Servico ID {registro.id} ('{registro.titulo}') inserido ao final da lista."
        return True

    def consultar_por_id(self, id_busca: int) -> Optional[RegistroServico]:
        """
        Realiza Busca Sequencial (Linear Search) percorrendo os ponteiros 'proximo' ate encontrar o ID.
        Complexidade:
            - Melhor caso: O(1) se o registro procurado estiver na cabeca da lista.
            - Caso medio: O(n) (em media n/2 comparacoes).
            - Pior caso: O(n) se estiver no ultimo no ou nao existir na lista.
            - Espaco auxiliar: O(1).
        """
        if not isinstance(id_busca, int) or isinstance(id_busca, bool):
            self.ultima_mensagem = "ID de busca invalido."
            return None

        atual = self.cabeca
        passos = 0
        while atual is not None:
            passos += 1
            if atual.dado.id == id_busca:
                self.ultima_mensagem = f"Servico ID {id_busca} localizado em {passos} passo(s)."
                return atual.dado
            atual = atual.proximo

        self.ultima_mensagem = f"Servico ID {id_busca} nao encontrado apos percorrer {passos} no(s)."
        return None

    # Alias compativel com nomenclatura alternativa
    consultar_id = consultar_por_id

    def listar_todos(self, exibir_no_terminal: bool = True) -> str:
        """
        Percorre todos os nos da lista encadeada do inicio (cabeca) ao fim (None)
        e formata a sequencia completa de registros e encadeamentos.
        Complexidade: O(n) em tempo e O(1) em espaco auxiliar de travessia.
        """
        if self.cabeca is None:
            mensagem = "  [Lista Vazia] Nenhum servico cadastrado na estrutura encadeada (cabeca -> None)."
            self.ultima_mensagem = mensagem
            if exibir_no_terminal:
                print(mensagem)
            return mensagem

        saida = ""
        atual = self.cabeca
        indice = 1
        while atual is not None:
            prox_indicador = f"ID {atual.proximo.dado.id:02d}" if atual.proximo is not None else "None"
            linha = (
                f"  {indice:02d}. {atual.dado.exibir_resumo()} "
                f"[prox -> {prox_indicador}]"
            )
            saida = saida + linha + "\n"
            atual = atual.proximo
            indice += 1

        rodape = f"  Total de registros na lista encadeada: {self.tamanho}"
        saida_completa = saida + rodape
        self.ultima_mensagem = rodape
        if exibir_no_terminal:
            print(saida_completa)
        return saida_completa

    def atualizar(self, id_busca: int, silencioso: bool = False, **campos: str) -> bool:
        """
        Localiza um registro pelo ID via travessia de ponteiros e atualiza os campos informados.
        Valida que nenhum campo atualizado receba valor vazio.
        Complexidade:
            - Melhor caso: O(1) quando o no atualizado e a cabeca.
            - Caso medio e pior caso: O(n) para localizar o no na lista.
            - Espaco auxiliar: O(1).
        """
        if self.cabeca is None:
            self.ultima_mensagem = "Operacao cancelada: a lista encadeada esta vazia."
            if not silencioso:
                print(f"  [!] {self.ultima_mensagem}")
            return False

        registro = self.consultar_por_id(id_busca)
        if registro is None:
            self.ultima_mensagem = f"Erro ao atualizar: servico com ID {id_busca} nao encontrado."
            if not silencioso:
                print(f"  [!] {self.ultima_mensagem}")
            return False

        campos_permitidos = (
            "titulo",
            "categoria",
            "descricao",
            "publico_alvo",
            "canal_atendimento",
        )
        if not campos:
            self.ultima_mensagem = "Nenhum campo foi informado para atualizacao."
            if not silencioso:
                print(f"  [!] {self.ultima_mensagem}")
            return False

        # Validacao previa de todos os campos antes de efetivar a mutacao
        for nome_campo, novo_valor in campos.items():
            if nome_campo not in campos_permitidos:
                self.ultima_mensagem = f"Erro: o atributo '{nome_campo}' nao pode ser alterado ou nao existe."
                if not silencioso:
                    print(f"  [!] {self.ultima_mensagem}")
                return False
            if not isinstance(novo_valor, str) or not novo_valor.strip():
                self.ultima_mensagem = f"Erro: o novo valor para '{nome_campo}' nao pode ser vazio."
                if not silencioso:
                    print(f"  [!] {self.ultima_mensagem}")
                return False

        for nome_campo, novo_valor in campos.items():
            setattr(registro, nome_campo, novo_valor.strip())

        self.ultima_mensagem = f"Servico ID {id_busca} atualizado com sucesso."
        return True

    def excluir(self, id_busca: int, silencioso: bool = False) -> Optional[RegistroServico]:
        """
        Remove o no correspondente ao 'id_busca' religando os ponteiros da estrutura encadeada.
        Trata explicitamente:
            1. Lista vazia (cabeca is None)
            2. Remocao no primeiro no (cabeca) -> O(1)
            3. Remocao em no intermediario (meio) -> O(n)
            4. Remocao no ultimo no (cauda) -> O(n)
            5. ID inexistente -> O(n)
        Espaco auxiliar: O(1).
        """
        if self.cabeca is None:
            self.ultima_mensagem = (
                f"Exclusao nao realizada: a lista esta vazia (tentativa de remover ID {id_busca})."
            )
            if not silencioso:
                print(f"  [!] {self.ultima_mensagem}")
            return None

        # Caso 1: O registro a ser excluido esta na cabeca da lista - O(1)
        if self.cabeca.dado.id == id_busca:
            no_removido = self.cabeca
            self.cabeca = self.cabeca.proximo
            no_removido.proximo = None
            self.tamanho -= 1
            self.ultima_mensagem = (
                f"Servico ID {id_busca} ('{no_removido.dado.titulo}') removido da CABECA da lista."
            )
            return no_removido.dado

        # Caso 2: Busca pelo no mantendo ponteiro para o no anterior
        anterior: NoServico = self.cabeca
        atual: Optional[NoServico] = self.cabeca.proximo

        while atual is not None:
            if atual.dado.id == id_busca:
                posicao = "CAUDA (fim)" if atual.proximo is None else "MEIO"
                anterior.proximo = atual.proximo
                atual.proximo = None
                self.tamanho -= 1
                self.ultima_mensagem = (
                    f"Servico ID {id_busca} ('{atual.dado.titulo}') removido do {posicao} da lista."
                )
                return atual.dado
            anterior = atual
            atual = atual.proximo

        self.ultima_mensagem = f"Erro ao excluir: servico ID {id_busca} nao existe na lista."
        if not silencioso:
            print(f"  [!] {self.ultima_mensagem}")
        return None

    # Alias compativel com nomenclatura alternativa
    remover_id = excluir

    def pesquisar_por_atributo(
        self, termo: str, campo: str = "titulo"
    ) -> ListaEncadeadaServicos:
        """
        Algoritmo proprio de Busca Linear (Sequencial) por substring normalizada (case-insensitive
        e sem acentos) sobre os campos 'titulo', 'categoria' ou 'ambos'.

        Retorna uma nova ListaEncadeadaServicos contendo os registros correspondentes,
        preservando a restricao de zero uso de listas nativas do Python.

        Complexidade:
            - Melhor caso, caso medio e pior caso: O(n), pois inspeciona todos os n nos
              da lista para encontrar todas as ocorrencias que satisfazem o filtro.
            - Espaco auxiliar de busca: O(1) alem dos k nos de resultado retornados.
        """
        resultados = ListaEncadeadaServicos()
        termo_norm = normalizar_texto(termo)
        campo_norm = normalizar_texto(campo)

        if not termo_norm:
            self.ultima_mensagem = "Termo de pesquisa vazio. Nenhum resultado retornado."
            return resultados

        if campo_norm not in ("titulo", "categoria", "ambos"):
            self.ultima_mensagem = (
                f"Campo '{campo}' invalido. Utilize 'titulo', 'categoria' ou 'ambos'."
            )
            return resultados

        cauda_resultado: Optional[NoServico] = None
        atual = self.cabeca

        while atual is not None:
            alvo_titulo = normalizar_texto(atual.dado.titulo)
            alvo_categoria = normalizar_texto(atual.dado.categoria)

            bateu = False
            if campo_norm == "titulo" and termo_norm in alvo_titulo:
                bateu = True
            elif campo_norm == "categoria" and termo_norm in alvo_categoria:
                bateu = True
            elif campo_norm == "ambos" and (
                termo_norm in alvo_titulo or termo_norm in alvo_categoria
            ):
                bateu = True

            if bateu:
                novo_no = NoServico(atual.dado.copiar())
                if resultados.cabeca is None:
                    resultados.cabeca = novo_no
                    cauda_resultado = novo_no
                else:
                    assert cauda_resultado is not None
                    cauda_resultado.proximo = novo_no
                    cauda_resultado = novo_no
                resultados.tamanho += 1

            atual = atual.proximo

        self.ultima_mensagem = (
            f"Pesquisa por '{termo}' no campo '{campo_norm}': "
            f"{resultados.tamanho} registro(s) encontrado(s)."
        )
        return resultados

    # Alias compativel com nomenclatura alternativa
    pesquisar = pesquisar_por_atributo

    def ordenar(self, criterio: str = "id") -> bool:
        """
        Ordena a Lista Encadeada utilizando o algoritmo Merge Sort adaptado para ponteiros.
        Manipula diretamente as referencias 'proximo' dos nos (in-place nos nos existentes),
        sem converter a estrutura para lista nativa do Python.

        Criterios aceitos:
            - 'id': Ordem numerica crescente pelo identificador unico.
            - 'titulo': Ordem alfabetica crescente pelo titulo normalizado (desempate por ID).

        Complexidade:
            - Melhor caso: O(n log n)
            - Caso medio: O(n log n)
            - Pior caso: O(n log n)
            - Espaco auxiliar: O(log n) devido a pilha de chamadas recursivas.
        """
        criterio_norm = normalizar_texto(criterio)
        if criterio_norm not in ("id", "titulo"):
            self.ultima_mensagem = (
                f"Criterio de ordenacao '{criterio}' invalido. Use 'id' ou 'titulo'."
            )
            return False

        if self.cabeca is None or self.cabeca.proximo is None:
            self.ultima_mensagem = (
                f"Lista com {self.tamanho} elemento(s) ja se encontra ordenada por '{criterio_norm}'."
            )
            return True

        self.cabeca = self._merge_sort_recursivo(self.cabeca, criterio_norm)
        self.ultima_mensagem = (
            f"Lista encadeada ordenada com sucesso por '{criterio_norm}' via Merge Sort O(n log n)."
        )
        return True

    @staticmethod
    def _dividir_ao_meio(cabeca: NoServico) -> Tuple[NoServico, Optional[NoServico]]:
        """
        Tecnica de dois ponteiros (Tartaruga e Lebre / Slow and Fast Pointer):
        O ponteiro 'rapido' avanca 2 nos por iteracao enquanto o 'lento' avanca 1 no.
        Quando 'rapido' atinge o final, 'lento' esta exatamente na metade da lista.
        Complexidade: O(n) em tempo e O(1) em espaco.
        """
        lento: NoServico = cabeca
        rapido: Optional[NoServico] = cabeca.proximo

        while rapido is not None and rapido.proximo is not None:
            assert lento.proximo is not None
            lento = lento.proximo
            rapido = rapido.proximo.proximo

        segunda_metade: Optional[NoServico] = lento.proximo
        lento.proximo = None  # Rompe o encadeamento dividindo em duas sublistas independentes
        return cabeca, segunda_metade

    @staticmethod
    def _precede(a: RegistroServico, b: RegistroServico, criterio: str) -> bool:
        """Retorna True se o registro 'a' deve vir antes ou igual ao registro 'b'."""
        if criterio == "titulo":
            chave_a = (normalizar_texto(a.titulo), a.id)
            chave_b = (normalizar_texto(b.titulo), b.id)
            return chave_a <= chave_b
        return a.id <= b.id

    @classmethod
    def _intercalar_listas_ordenadas(
        cls,
        esquerda: Optional[NoServico],
        direita: Optional[NoServico],
        criterio: str,
    ) -> Optional[NoServico]:
        """
        Intercala (merge) duas sublistas encadeadas ja ordenadas religando os ponteiros
        'proximo' de forma iterativa com um no sentinela temporario.
        Complexidade: O(n + m) em tempo e O(1) em espaco auxiliar (evita recursao profunda no merge).
        """
        if esquerda is None:
            return direita
        if direita is None:
            return esquerda

        sentinela = NoServico(
            RegistroServico(0, "SENTINELA", "SISTEMA", "SENTINELA", "SISTEMA", "SISTEMA")
        )
        cauda = sentinela

        p_esq: Optional[NoServico] = esquerda
        p_dir: Optional[NoServico] = direita

        while p_esq is not None and p_dir is not None:
            if cls._precede(p_esq.dado, p_dir.dado, criterio):
                cauda.proximo = p_esq
                p_esq = p_esq.proximo
            else:
                cauda.proximo = p_dir
                p_dir = p_dir.proximo
            cauda = cauda.proximo

        # Anexa o restante da sublista que ainda possuir nos
        cauda.proximo = p_esq if p_esq is not None else p_dir
        return sentinela.proximo

    @classmethod
    def _merge_sort_recursivo(
        cls, cabeca: Optional[NoServico], criterio: str
    ) -> Optional[NoServico]:
        """Executa a divisao e conquista recursiva do Merge Sort sobre os ponteiros."""
        if cabeca is None or cabeca.proximo is None:
            return cabeca

        metade_esq, metade_dir = cls._dividir_ao_meio(cabeca)
        esq_ordenada = cls._merge_sort_recursivo(metade_esq, criterio)
        dir_ordenada = cls._merge_sort_recursivo(metade_dir, criterio)

        return cls._intercalar_listas_ordenadas(esq_ordenada, dir_ordenada, criterio)


def popular_dados_iniciais(lista: ListaEncadeadaServicos) -> int:
    """
    Carrega os servicos publicos oficiais da Central do Cidadao de Aurora (Fichas FC-01 a FC-07
    e modulo de Transicao Energetica ERS-01 a ERS-03).
    Os registros sao inseridos em uma ordem inicial propositalmente nao ordenada por ID/titulo
    para demonstrar com clareza o funcionamento do algoritmo Merge Sort em ponteiros.
    """
    # Insercao encadeada sem uso de listas nativas: cada chamada adiciona um NoServico direto na lista
    inseridos = 0

    if lista.inserir(
        RegistroServico(
            id=7,
            titulo="Agendamento, Horarios e Pagamento de Taxas (FC-07)",
            categoria="Atendimento e Direitos",
            descricao=(
                "Atendimento presencial de segunda a sexta, das 8h as 17h (fechado aos sabados, "
                "domingos e feriados). Taxas pagas via guia do portal em banco ou PIX (compensa em 2 dias uteis)."
            ),
            publico_alvo="Todos os cidadaos de Aurora; prioridade legal para 60+, gestantes e PcD.",
            canal_atendimento="Portal da Central do Cidadao de Aurora e Balcao Presencial.",
        ),
        silencioso=True,
    ):
        inseridos += 1

    if lista.inserir(
        RegistroServico(
            id=1,
            titulo="Carteira de Identidade - RG: 1a e 2a Via (FC-01)",
            categoria="Documentos",
            descricao=(
                "1a via gratuita; 2a via custa R$ 38,00 com agendamento obrigatorio. Exige Certidao "
                "original/autenticada, comprovante de residencia (90 dias) e B.O. (roubo/furto) ou Declaracao (perda)."
            ),
            publico_alvo="Qualquer cidadao; menores de 12 anos acompanhados de responsavel legal com foto.",
            canal_atendimento="Posto de Identificacao de Aurora (entrega em 10 dias uteis).",
        ),
        silencioso=True,
    ):
        inseridos += 1

    if lista.inserir(
        RegistroServico(
            id=5,
            titulo="Certidoes de Nascimento, Casamento e Obito - 2a Via (FC-05)",
            categoria="Documentos",
            descricao=(
                "1a via gratuita no cartorio. 2a via na Central por R$ 45,00 (isencao para inscritos no "
                "CadUnico com NIS ativo). Prazo de emissao de 5 dias uteis."
            ),
            publico_alvo="Titular maior de 18 anos, responsavel legal ou procurador com procuracao simples.",
            canal_atendimento="Balcao de Registro Civil da Central de Aurora ou Portal Digital.",
        ),
        silencioso=True,
    ):
        inseridos += 1

    if lista.inserir(
        RegistroServico(
            id=10,
            titulo="Energia Solar Fotovoltaica e Geracao Compartilhada (ERS-03)",
            categoria="Energia e Sustentabilidade",
            descricao=(
                "Orientacao tecnico-economica para geracao distribuida solar (kit 2,0 kWp On-Grid com "
                "payback de 3,6 anos) ou assinatura de Geracao Compartilhada sem obras para inquilinos."
            ),
            publico_alvo="Proprietarios residenciais e inquilinos atendidos pela Central de Aurora.",
            canal_atendimento="Nucleo de Transicao Energetica Cidada de Aurora e Assistente Digital.",
        ),
        silencioso=True,
    ):
        inseridos += 1

    if lista.inserir(
        RegistroServico(
            id=3,
            titulo="Titulo de Eleitor: Emissao, Revisao e Transferencia (FC-03)",
            categoria="Documentos",
            descricao=(
                "Servico gratuito com emissao imediata no e-Titulo. Exige documento oficial com foto, "
                "comprovante de residencia (minimo 3 meses no municipio) e quitacao militar (homens de 18 a 45 anos)."
            ),
            publico_alvo="Obrigatorio dos 18 aos 70 anos; facultativo para jovens de 16/17 anos, 70+ e analfabetos.",
            canal_atendimento="Portal Titulo Net (TSE) ou Posto Eleitoral da Central de Aurora.",
        ),
        silencioso=True,
    ):
        inseridos += 1

    if lista.inserir(
        RegistroServico(
            id=8,
            titulo="Acessibilidade, Atendimento Prioritario e Interprete de Libras (FC-07)",
            categoria="Atendimento e Direitos",
            descricao=(
                "Garantia de fila prioritaria em todos os guiches e totem IoT, alem de atendimento "
                "com interprete de Libras mediante agendamento previo com 48 horas de antecedencia."
            ),
            publico_alvo="Idosos (60+ anos), gestantes, lactantes, pessoas com mobilidade reduzida e PcD.",
            canal_atendimento="Todos os postos presenciais da Central do Cidadao de Aurora.",
        ),
        silencioso=True,
    ):
        inseridos += 1

    if lista.inserir(
        RegistroServico(
            id=2,
            titulo="CPF: Inscricao, Regularizacao Cadastral e 2a Via (FC-02)",
            categoria="Documentos",
            descricao=(
                "Servico gratuito e imediato (exceto regularizacao com pendencia na Receita Federal, "
                "que leva ate 2 dias uteis). Exige documento com foto e certidao de nascimento/casamento."
            ),
            publico_alvo="Qualquer pessoa fisica, inclusive recem-nascidos e estrangeiros residentes.",
            canal_atendimento="Site da Receita Federal ou Guiche de Atendimento Rapido da Central de Aurora.",
        ),
        silencioso=True,
    ):
        inseridos += 1

    if lista.inserir(
        RegistroServico(
            id=6,
            titulo="CNH: Renovacao, Prazos de Validade e Exame Medico (FC-06)",
            categoria="Trabalho e Mobilidade",
            descricao=(
                "Agendamento obrigatorio. Taxa de renovacao de R$ 116,50 + exame medico em clinica "
                "credenciada. Validade: 10 anos (<50 anos), 5 anos (50 a 69 anos) e 3 anos (70+ anos)."
            ),
            publico_alvo="Condutores habilitados com CNH vencida ou a vencer em ate 30 dias.",
            canal_atendimento="Posto do Detran na Central de Aurora (CNH Digital liberada em 3 dias uteis).",
        ),
        silencioso=True,
    ):
        inseridos += 1

    if lista.inserir(
        RegistroServico(
            id=9,
            titulo="Diagnostico de Consumo Eletrico e Eficiencia Procel/LED (ERS-01/02)",
            categoria="Energia e Sustentabilidade",
            descricao=(
                "Simulacao de consumo mensal em kWh (chuveiro, refrigeracao e iluminacao) e plano de "
                "substituicao por lampadas LED Procel A (9W), reduzindo ate 107,5 kWh/mes com payback de 1 mes."
            ),
            publico_alvo="Familias do municipio de Aurora que buscam reducao imediata na fatura de energia.",
            canal_atendimento="Nucleo de Transicao Energetica Cidada de Aurora e Assistente Digital.",
        ),
        silencioso=True,
    ):
        inseridos += 1

    if lista.inserir(
        RegistroServico(
            id=4,
            titulo="Carteira de Trabalho Digital - CTPS (FC-04)",
            categoria="Trabalho e Mobilidade",
            descricao=(
                "Emissao 100% gratuita e imediata vinculada ao numero do CPF via conta Gov.br. "
                "A via fisica em papel nao e mais emitida, salvo excecoes de orgaos publicos internacionais."
            ),
            publico_alvo="Cidadaos a partir de 14 anos (na condicao de Jovem Aprendiz) ou trabalhadores em geral.",
            canal_atendimento="Aplicativo Carteira de Trabalho Digital ou Balcao de Apoio Gov.br em Aurora.",
        ),
        silencioso=True,
    ):
        inseridos += 1

    return inseridos


def executar_bateria_testes_evidencias() -> str:
    """
    Executa a bateria completa de testes funcionais e estruturais exigida na rubrica de DSA,
    registrando todas as evidencias de entrada, processamento e saida em log textual.
    """
    log_buffer = ""

    def registrar_linha(texto: str = "") -> None:
        nonlocal log_buffer
        print(texto)
        log_buffer = log_buffer + texto + "\n"

    separador = "=" * 92
    sub_sep = "-" * 92

    registrar_linha(separador)
    registrar_linha("  EVIDENCIAS DE TESTES AUTOMATIZADOS - DATA STRUCTURES AND ALGORITHMS (DSA)")
    registrar_linha("  Estrutura: Lista Simplesmente Encadeada Propria (NoServico / ListaEncadeadaServicos)")
    registrar_linha("  Universo: Central do Cidadao de Aurora (Fichas FC-01 a FC-07 + Energia Sustentavel)")
    registrar_linha(separador)

    lista = ListaEncadeadaServicos()

    # -------------------------------------------------------------------------
    # TESTE 1: OPERACOES SOBRE LISTA VAZIA (CASO LIMITE OBRIGATORIO)
    # -------------------------------------------------------------------------
    registrar_linha("\n[TESTE 1] Operacoes sobre a Estrutura em Estado Vazio (cabeca = None, tamanho = 0)")
    registrar_linha(sub_sep)
    registrar_linha(f"  -> Estado inicial: esta_vazia() = {lista.esta_vazia()} | tamanho = {len(lista)}")
    registrar_linha("  -> 1.1. Tentativa de listar todos em lista vazia:")
    registrar_linha(lista.listar_todos(exibir_no_terminal=False))

    consulta_vazia = lista.consultar_por_id(1)
    registrar_linha(
        f"  -> 1.2. Consultar ID 1 em lista vazia: retorno = {consulta_vazia} | msg = '{lista.ultima_mensagem}'"
    )

    atualiza_vazia = lista.atualizar(1, silencioso=True, titulo="Novo Titulo")
    registrar_linha(
        f"  -> 1.3. Atualizar ID 1 em lista vazia: retorno = {atualiza_vazia} | msg = '{lista.ultima_mensagem}'"
    )

    exclui_vazia = lista.excluir(1, silencioso=True)
    registrar_linha(
        f"  -> 1.4. Excluir ID 1 em lista vazia  : retorno = {exclui_vazia} | msg = '{lista.ultima_mensagem}'"
    )

    pesquisa_vazia = lista.pesquisar_por_atributo("RG", campo="titulo")
    registrar_linha(
        f"  -> 1.5. Pesquisar 'RG' em lista vazia: encontrados = {len(pesquisa_vazia)} | msg = '{lista.ultima_mensagem}'"
    )

    ordena_vazia = lista.ordenar(criterio="id")
    registrar_linha(
        f"  -> 1.6. Ordenar lista vazia por ID   : retorno = {ordena_vazia} | msg = '{lista.ultima_mensagem}'"
    )

    assert lista.esta_vazia() and len(lista) == 0, "Falha no Teste 1: lista deveria permanecer vazia."

    # -------------------------------------------------------------------------
    # TESTE 2: INSERCAO DE MULTIPLOS REGISTROS E LISTAGEM DO ENCADEAMENTO
    # -------------------------------------------------------------------------
    registrar_linha("\n[TESTE 2] Insercao de Multiplos Registros na Lista Encadeada (Ordem Inicial Embaralhada)")
    registrar_linha(sub_sep)
    qtd_inserida = popular_dados_iniciais(lista)
    registrar_linha(f"  -> Registros inseridos via popular_dados_iniciais(): {qtd_inserida}")
    registrar_linha(f"  -> Estado atual: esta_vazia() = {lista.esta_vazia()} | tamanho = {len(lista)}")
    registrar_linha("  -> Sequencia atual de nos e ponteiros (cabeca -> ... -> None):")
    registrar_linha(lista.listar_todos(exibir_no_terminal=False))

    assert len(lista) == 10, "Falha no Teste 2: esperado 10 registros iniciais."

    # -------------------------------------------------------------------------
    # TESTE 3: VALIDACAO DE CAMPOS OBRIGATORIOS E REJEICAO DE ID DUPLICADO
    # -------------------------------------------------------------------------
    registrar_linha("\n[TESTE 3] Validacao de Integridade: Rejeicao de ID Duplicado e Campos Vazios")
    registrar_linha(sub_sep)

    dup_ok = lista.inserir(
        RegistroServico(
            id=1,
            titulo="Servico Duplicado Invalido",
            categoria="Documentos",
            descricao="Tentativa de sobrescrever ID 1.",
            publico_alvo="Qualquer pessoa",
            canal_atendimento="Balcao",
        ),
        silencioso=True,
    )
    registrar_linha(f"  -> 3.1. Inserir ID=1 ja existente : aceito = {dup_ok} | msg = '{lista.ultima_mensagem}'")

    vazio_ok = lista.inserir(
        RegistroServico(
            id=99,
            titulo="   ",
            categoria="Documentos",
            descricao="Registro sem titulo.",
            publico_alvo="Cidadaos",
            canal_atendimento="Portal",
        ),
        silencioso=True,
    )
    registrar_linha(f"  -> 3.2. Inserir titulo em branco  : aceito = {vazio_ok} | msg = '{lista.ultima_mensagem}'")

    id_neg_ok = lista.inserir(
        RegistroServico(
            id=-5,
            titulo="Servico com ID Negativo",
            categoria="Documentos",
            descricao="Teste de ID invalido.",
            publico_alvo="Cidadaos",
            canal_atendimento="Portal",
        ),
        silencioso=True,
    )
    registrar_linha(f"  -> 3.3. Inserir ID=-5 (negativo)  : aceito = {id_neg_ok} | msg = '{lista.ultima_mensagem}'")
    registrar_linha(f"  -> Tamanho preservado apos rejeicoes: {len(lista)} registros.")

    assert not dup_ok and not vazio_ok and not id_neg_ok and len(lista) == 10

    # -------------------------------------------------------------------------
    # TESTE 4: CONSULTA POR ID (EXISTENTE E INEXISTENTE)
    # -------------------------------------------------------------------------
    registrar_linha("\n[TESTE 4] Consulta Sequencial por ID (Existente vs. Inexistente)")
    registrar_linha(sub_sep)
    reg_id3 = lista.consultar_por_id(3)
    registrar_linha(f"  -> 4.1. Busca por ID = 3 : {lista.ultima_mensagem}")
    if reg_id3 is not None:
        registrar_linha(reg_id3.exibir_detalhado())

    reg_id999 = lista.consultar_por_id(999)
    registrar_linha(
        f"  -> 4.2. Busca por ID = 999 (inexistente): retorno = {reg_id999} | {lista.ultima_mensagem}"
    )

    assert reg_id3 is not None and reg_id3.id == 3 and reg_id999 is None

    # -------------------------------------------------------------------------
    # TESTE 5: ATUALIZACAO DE REGISTRO (ESTADO ANTES E DEPOIS)
    # -------------------------------------------------------------------------
    registrar_linha("\n[TESTE 5] Atualizacao de Registro Existente (Demonstracao Antes e Depois)")
    registrar_linha(sub_sep)
    antes_id2 = lista.consultar_por_id(2)
    assert antes_id2 is not None
    registrar_linha("  -> [ANTES DA ATUALIZACAO - ID 2]:")
    registrar_linha(antes_id2.exibir_detalhado())

    atualizou = lista.atualizar(
        2,
        silencioso=True,
        canal_atendimento="Portal Receita Federal, App Gov.br e Guiche Expresso da Central de Aurora.",
        descricao=(
            "Inscricao, 2a via e comprovante gratuitos na hora; regularizacao cadastral em ate "
            "2 dias uteis com protocolo digital."
        ),
    )
    registrar_linha(f"\n  -> Status da operacao atualizar(id=2): {atualizou} ({lista.ultima_mensagem})")
    depois_id2 = lista.consultar_por_id(2)
    assert depois_id2 is not None
    registrar_linha("  -> [DEPOIS DA ATUALIZACAO - ID 2]:")
    registrar_linha(depois_id2.exibir_detalhado())

    assert atualizou and "Guiche Expresso" in depois_id2.canal_atendimento

    # -------------------------------------------------------------------------
    # TESTE 6: PESQUISA LINEAR POR ATRIBUTO (TITULO E CATEGORIA)
    # -------------------------------------------------------------------------
    registrar_linha("\n[TESTE 6] Pesquisa Linear por Atributo (Normalizada Case-Insensitive / Sem Acentos)")
    registrar_linha(sub_sep)

    res_titulo = lista.pesquisar_por_atributo("identidade", campo="titulo")
    registrar_linha(f"  -> 6.1. {lista.ultima_mensagem}")
    registrar_linha(res_titulo.listar_todos(exibir_no_terminal=False))

    res_categoria = lista.pesquisar_por_atributo("energia", campo="categoria")
    registrar_linha(f"\n  -> 6.2. {lista.ultima_mensagem}")
    registrar_linha(res_categoria.listar_todos(exibir_no_terminal=False))

    res_inexistente = lista.pesquisar_por_atributo("passaporte diplomatico", campo="ambos")
    registrar_linha(f"\n  -> 6.3. {lista.ultima_mensagem}")
    registrar_linha(res_inexistente.listar_todos(exibir_no_terminal=False))

    assert len(res_titulo) == 1 and len(res_categoria) == 2 and len(res_inexistente) == 0

    # -------------------------------------------------------------------------
    # TESTE 7: ORDENACAO MERGE SORT EM PONTEIROS (POR TITULO E POR ID)
    # -------------------------------------------------------------------------
    registrar_linha("\n[TESTE 7] Ordenacao Merge Sort em Lista Encadeada O(n log n) - Sem Listas Nativas")
    registrar_linha(sub_sep)

    lista.ordenar(criterio="titulo")
    registrar_linha(f"  -> 7.1. {lista.ultima_mensagem}")
    registrar_linha("  -> Lista encadeada apos ordenacao alfabetica por TITULO:")
    registrar_linha(lista.listar_todos(exibir_no_terminal=False))

    # Verificacao de monotonia alfabetica percorrendo os ponteiros
    atual_verif = lista.cabeca
    while atual_verif is not None and atual_verif.proximo is not None:
        t1 = normalizar_texto(atual_verif.dado.titulo)
        t2 = normalizar_texto(atual_verif.proximo.dado.titulo)
        assert t1 <= t2, f"Erro de ordenacao por titulo: {t1} > {t2}"
        atual_verif = atual_verif.proximo

    lista.ordenar(criterio="id")
    registrar_linha(f"\n  -> 7.2. {lista.ultima_mensagem}")
    registrar_linha("  -> Lista encadeada apos ordenacao numerica crescente por ID:")
    registrar_linha(lista.listar_todos(exibir_no_terminal=False))

    # Verificacao de monotonia crescente por ID percorrendo os ponteiros
    atual_verif = lista.cabeca
    id_esperado = 1
    while atual_verif is not None:
        assert atual_verif.dado.id == id_esperado, (
            f"Erro de ordenacao por ID: esperado {id_esperado}, obtido {atual_verif.dado.id}"
        )
        id_esperado += 1
        atual_verif = atual_verif.proximo

    # -------------------------------------------------------------------------
    # TESTE 8: EXCLUSAO DE REGISTROS (CABECA, MEIO, CAUDA E INEXISTENTE)
    # -------------------------------------------------------------------------
    registrar_linha("\n[TESTE 8] Exclusao de Nos e Religacao de Ponteiros (Cabeca, Meio, Cauda e Inexistente)")
    registrar_linha(sub_sep)

    rem_cabeca = lista.excluir(1, silencioso=True)
    registrar_linha(f"  -> 8.1. Remover ID 1 (Cabeca) : {lista.ultima_mensagem}")

    rem_meio = lista.excluir(5, silencioso=True)
    registrar_linha(f"  -> 8.2. Remover ID 5 (Meio)   : {lista.ultima_mensagem}")

    rem_cauda = lista.excluir(10, silencioso=True)
    registrar_linha(f"  -> 8.3. Remover ID 10 (Cauda) : {lista.ultima_mensagem}")

    rem_inex = lista.excluir(500, silencioso=True)
    registrar_linha(f"  -> 8.4. Remover ID 500 (Inex.): retorno = {rem_inex} | {lista.ultima_mensagem}")

    registrar_linha("\n  -> Estado final da Lista Encadeada apos as 3 exclusoes (7 nos restantes):")
    registrar_linha(lista.listar_todos(exibir_no_terminal=False))

    assert (
        rem_cabeca is not None
        and rem_meio is not None
        and rem_cauda is not None
        and rem_inex is None
        and len(lista) == 7
        and lista.cabeca is not None
        and lista.cabeca.dado.id == 2
    )

    registrar_linha(separador)
    registrar_linha("  RESULTADO FINAL DA BATERIA DE TESTES DSA: 100% APROVADO (ZERO ERROS)")
    registrar_linha(separador)

    return log_buffer


def _ler_inteiro_seguro(prompt_msg: str) -> Optional[int]:
    """Le um numero inteiro do terminal tratando ValueError sem encerrar o programa."""
    try:
        entrada = input(prompt_msg).strip()
        if not entrada:
            print("  [!] Entrada vazia. Digite um numero inteiro valido.")
            return None
        return int(entrada)
    except ValueError:
        print("  [!] Entrada invalida: digite apenas algarismos numericos inteiros.")
        return None
    except (EOFError, KeyboardInterrupt):
        return None


def executar_menu_dsa(lista_existente: Optional[ListaEncadeadaServicos] = None) -> None:
    """
    Interface interativa em terminal para operacao completa do sistema CRUD em Lista Encadeada.
    Trata entradas invalidas de forma segura sem interromper a execucao.
    """
    if lista_existente is not None:
        lista = lista_existente
    else:
        lista = ListaEncadeadaServicos()
        popular_dados_iniciais(lista)

    while True:
        print("\n" + "=" * 78)
        print("  CENTRAL DO CIDADAO DE AURORA - CATALOGO DE SERVICOS (LISTA ENCADEADA DSA)")
        print("=" * 78)
        print(f"  Registros atualmente encadeados: {len(lista)} | Cabeca: "
              f"{'ID ' + str(lista.cabeca.dado.id) if lista.cabeca else 'None (Lista Vazia)'}")
        print("-" * 78)
        print("  [1] Listar todos os servicos (percorrer ponteiros da Lista Encadeada)")
        print("  [2] Inserir novo servico publico")
        print("  [3] Consultar servico por ID (Busca Sequencial)")
        print("  [4] Atualizar servico existente por ID")
        print("  [5] Excluir servico por ID (Religacao de ponteiros)")
        print("  [6] Pesquisar servicos por Titulo ou Categoria (Busca Linear Normalizada)")
        print("  [7] Ordenar Lista Encadeada via Merge Sort O(n log n) (por ID ou Titulo)")
        print("  [8] Executar bateria completa de testes e evidencias automatizadas")
        print("  [9] Esvaziar lista ou restaurar base inicial da Central de Aurora")
        print("  [0] Voltar / Encerrar modulo DSA")
        print("-" * 78)

        try:
            opcao = input("  Escolha uma opcao [0-9]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Encerrando modulo DSA...")
            break

        if opcao == "0":
            print("  Saindo do modulo de Lista Encadeada (DSA). Ate logo!")
            break

        elif opcao == "1":
            print("\n--- LISTAGEM COMPLETA DOS NOS ENCADEADOS ---")
            lista.listar_todos(exibir_no_terminal=True)

        elif opcao == "2":
            print("\n--- INSERIR NOVO SERVICO PUBLICO ---")
            novo_id = _ler_inteiro_seguro("  ID numerico positivo do servico: ")
            if novo_id is None:
                continue
            try:
                titulo = input("  Titulo do servico: ").strip()
                categoria = input("  Categoria (ex: Documentos, Atendimento e Direitos): ").strip()
                descricao = input("  Descricao detalhada (regras, taxas, prazos): ").strip()
                publico = input("  Publico-alvo: ").strip()
                canal = input("  Canal de atendimento: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n  Operacao cancelada.")
                continue

            novo_reg = RegistroServico(
                id=novo_id,
                titulo=titulo,
                categoria=categoria,
                descricao=descricao,
                publico_alvo=publico,
                canal_atendimento=canal,
            )
            if lista.inserir(novo_reg, silencioso=False):
                print(f"  [OK] {lista.ultima_mensagem}")

        elif opcao == "3":
            print("\n--- CONSULTAR SERVICO POR ID ---")
            id_busca = _ler_inteiro_seguro("  Informe o ID do servico que deseja consultar: ")
            if id_busca is None:
                continue
            encontrado = lista.consultar_por_id(id_busca)
            print(f"  Status: {lista.ultima_mensagem}")
            if encontrado is not None:
                print("-" * 60)
                print(encontrado.exibir_detalhado())
                print("-" * 60)

        elif opcao == "4":
            print("\n--- ATUALIZAR SERVICO POR ID ---")
            if lista.esta_vazia():
                print("  [!] A lista encadeada esta vazia. Insira registros antes de atualizar.")
                continue
            id_busca = _ler_inteiro_seguro("  Informe o ID do servico a ser atualizado: ")
            if id_busca is None:
                continue
            atual = lista.consultar_por_id(id_busca)
            if atual is None:
                print(f"  [!] Servico com ID {id_busca} nao encontrado na lista.")
                continue

            print("\n  Estado atual do registro:")
            print(atual.exibir_detalhado())
            print("\n  (Deixe em branco e pressione ENTER nos campos que desejar manter inalterados)")
            try:
                novo_titulo = input(f"  Novo titulo [{atual.titulo}]: ").strip()
                nova_cat = input(f"  Nova categoria [{atual.categoria}]: ").strip()
                nova_desc = input("  Nova descricao: ").strip()
                novo_pub = input(f"  Novo publico-alvo [{atual.publico_alvo}]: ").strip()
                novo_canal = input(f"  Novo canal [{atual.canal_atendimento}]: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n  Operacao cancelada.")
                continue

            campos_para_atualizar = {}
            if novo_titulo:
                campos_para_atualizar["titulo"] = novo_titulo
            if nova_cat:
                campos_para_atualizar["categoria"] = nova_cat
            if nova_desc:
                campos_para_atualizar["descricao"] = nova_desc
            if novo_pub:
                campos_para_atualizar["publico_alvo"] = novo_pub
            if novo_canal:
                campos_para_atualizar["canal_atendimento"] = novo_canal

            if not campos_para_atualizar:
                print("  [i] Nenhuma alteracao informada. Registro mantido original.")
            elif lista.atualizar(id_busca, silencioso=False, **campos_para_atualizar):
                print(f"  [OK] {lista.ultima_mensagem}")
                print("\n  Estado atualizado do registro:")
                print(atual.exibir_detalhado())

        elif opcao == "5":
            print("\n--- EXCLUIR SERVICO POR ID ---")
            id_busca = _ler_inteiro_seguro("  Informe o ID do servico a ser removido: ")
            if id_busca is None:
                continue
            removido = lista.excluir(id_busca, silencioso=False)
            if removido is not None:
                print(f"  [OK] {lista.ultima_mensagem}")

        elif opcao == "6":
            print("\n--- PESQUISAR SERVICOS POR ATRIBUTO ---")
            try:
                campo = input("  Campo de busca ('titulo', 'categoria' ou 'ambos') [titulo]: ").strip()
                if not campo:
                    campo = "titulo"
                termo = input("  Digite o termo de pesquisa: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n  Operacao cancelada.")
                continue

            resultados = lista.pesquisar_por_atributo(termo, campo=campo)
            print(f"\n  {lista.ultima_mensagem}")
            if not resultados.esta_vazia():
                resultados.listar_todos(exibir_no_terminal=True)

        elif opcao == "7":
            print("\n--- ORDENAR LISTA ENCADEADA (MERGE SORT EM PONTEIROS) ---")
            try:
                criterio = input("  Escolha o criterio ('id' ou 'titulo') [id]: ").strip()
                if not criterio:
                    criterio = "id"
            except (EOFError, KeyboardInterrupt):
                print("\n  Operacao cancelada.")
                continue

            if lista.ordenar(criterio=criterio):
                print(f"  [OK] {lista.ultima_mensagem}")
                lista.listar_todos(exibir_no_terminal=True)
            else:
                print(f"  [!] {lista.ultima_mensagem}")

        elif opcao == "8":
            print()
            executar_bateria_testes_evidencias()

        elif opcao == "9":
            print("\n--- GERENCIAR ESTADO DA LISTA ---")
            print("  [1] Esvaziar completamente a lista (cabeca = None) para testar lista vazia")
            print("  [2] Restaurar os 10 servicos padrao da Central de Aurora")
            try:
                sub = input("  Escolha [1/2]: ").strip()
            except (EOFError, KeyboardInterrupt):
                continue
            if sub == "1":
                lista.cabeca = None
                lista.tamanho = 0
                print("  [OK] Lista encadeada esvaziada (0 elementos).")
            elif sub == "2":
                lista.cabeca = None
                lista.tamanho = 0
                qtd = popular_dados_iniciais(lista)
                print(f"  [OK] Base inicial restaurada com {qtd} servicos encadeados.")
            else:
                print("  [!] Sub-opcao invalida.")

        else:
            print(f"  [!] Opcao '{opcao}' invalida. Escolha um numero de 0 a 9.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--test", "-t"):
        executar_bateria_testes_evidencias()
    else:
        executar_menu_dsa()
