import { useEffect, useState } from 'react'
import {
  ArrowLeft,
  CalendarDays,
  CheckCircle2,
  FileSpreadsheet,
  RefreshCw,
} from 'lucide-react'

type Indicadores = {
  faturamento: number
  vendas: number
  ticket_medio: number
  clientes_unicos: number
}

type Processamento = {
  id: number
  arquivo: string
  criado_em: string
  status: string
  periodo_inicio: string | null
  periodo_fim: string | null
  indicadores: Indicadores | null
  erro: string | null
}

type DetalhesProcessamento = Processamento & {
  filtros: {
    data_inicio: string | null
    data_fim: string | null
    produto: string | null
  } | null

  resumo_limpeza: {
    linhas_lidas: number
    duplicadas_removidas: number
    campos_corrigidos: number
  } | null
}

function moeda(valor: number) {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(valor)
}

function dataHora(valor: string) {
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(valor))
}

export default function Historico() {
  const [processamentos, setProcessamentos] = useState<Processamento[]>([])
  const [detalhes, setDetalhes] = useState<DetalhesProcessamento | null>(null)

  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState('')

  async function carregarHistorico() {
    setCarregando(true)
    setErro('')

    try {
      const resposta = await fetch('/api/historico')

      if (!resposta.ok) {
        throw new Error('Não foi possível carregar o histórico.')
      }

      const dados = await resposta.json()

      setProcessamentos(dados.processamentos)
    } catch (error) {
      setErro(
        error instanceof Error
          ? error.message
          : 'Erro ao carregar histórico.'
      )
    } finally {
      setCarregando(false)
    }
  }

  async function abrirDetalhes(id: number) {
    setErro('')

    try {
      const resposta = await fetch(`/api/historico/${id}`)

      if (!resposta.ok) {
        throw new Error('Não foi possível abrir esse processamento.')
      }

      const dados = await resposta.json()

      setDetalhes(dados)
    } catch (error) {
      setErro(
        error instanceof Error
          ? error.message
          : 'Erro ao carregar os detalhes.'
      )
    }
  }

  useEffect(() => {
    void carregarHistorico()
  }, [])

  if (detalhes) {
    return (
      <div>
        <button
          type="button"
          onClick={() => setDetalhes(null)}
          className="mb-6 flex items-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-700"
        >
          <ArrowLeft size={18} />
          Voltar ao histórico
        </button>

        <div className="mb-6">
          <p className="text-sm font-medium text-blue-600">
            Processamento #{detalhes.id}
          </p>

          <h1 className="mt-1 text-3xl font-bold">
            {detalhes.arquivo}
          </h1>

          <p className="mt-2 text-sm text-slate-500">
            {dataHora(detalhes.criado_em)}
          </p>
        </div>

        <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-slate-500">Faturamento</p>
            <p className="mt-3 text-xl font-bold">
              {moeda(detalhes.indicadores?.faturamento ?? 0)}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-slate-500">Vendas</p>
            <p className="mt-3 text-xl font-bold">
              {detalhes.indicadores?.vendas ?? 0}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-slate-500">Ticket médio</p>
            <p className="mt-3 text-xl font-bold">
              {moeda(detalhes.indicadores?.ticket_medio ?? 0)}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-slate-500">Clientes únicos</p>
            <p className="mt-3 text-xl font-bold">
              {detalhes.indicadores?.clientes_unicos ?? 0}
            </p>
          </div>
        </section>

        <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="font-semibold">Detalhes da execução</h2>

          <div className="mt-5 grid gap-5 md:grid-cols-2">
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-400">
                Período
              </p>

              <p className="mt-1 text-sm">
                {detalhes.periodo_inicio ?? '—'}
                {' até '}
                {detalhes.periodo_fim ?? '—'}
              </p>
            </div>

            <div>
              <p className="text-xs uppercase tracking-wide text-slate-400">
                Produto filtrado
              </p>

              <p className="mt-1 text-sm">
                {detalhes.filtros?.produto || 'Todos os produtos'}
              </p>
            </div>

            <div>
              <p className="text-xs uppercase tracking-wide text-slate-400">
                Linhas lidas
              </p>

              <p className="mt-1 text-sm">
                {detalhes.resumo_limpeza?.linhas_lidas ?? 0}
              </p>
            </div>

            <div>
              <p className="text-xs uppercase tracking-wide text-slate-400">
                Duplicatas removidas
              </p>

              <p className="mt-1 text-sm">
                {detalhes.resumo_limpeza?.duplicadas_removidas ?? 0}
              </p>
            </div>
          </div>
        </section>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="text-sm font-medium text-blue-600">
            Execuções anteriores
          </p>

          <h1 className="mt-1 text-3xl font-bold">
            Histórico
          </h1>

          <p className="mt-2 text-sm text-slate-500">
            Consulte os relatórios já processados pelo DataFlow.
          </p>
        </div>

        <button
          type="button"
          onClick={() => void carregarHistorico()}
          disabled={carregando}
          className="flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium hover:bg-slate-50 disabled:opacity-50"
        >
          <RefreshCw
            size={17}
            className={carregando ? 'animate-spin' : ''}
          />

          Atualizar
        </button>
      </div>

      {erro && (
        <div className="mb-5 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {erro}
        </div>
      )}

      {carregando ? (
        <div className="rounded-2xl border border-slate-200 bg-white p-10 text-center text-sm text-slate-500">
          Carregando histórico...
        </div>
      ) : processamentos.length === 0 ? (
        <div className="rounded-2xl border border-slate-200 bg-white p-10 text-center">
          <FileSpreadsheet
            size={36}
            className="mx-auto text-slate-300"
          />

          <p className="mt-4 font-medium">
            Nenhum processamento encontrado
          </p>

          <p className="mt-1 text-sm text-slate-500">
            Seus relatórios processados aparecerão aqui.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {processamentos.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => void abrirDetalhes(item.id)}
              className="w-full rounded-2xl border border-slate-200 bg-white p-5 text-left shadow-sm transition hover:border-blue-200 hover:shadow-md"
            >
              <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
                <div className="flex min-w-0 items-center gap-4">
                  <div className="rounded-xl bg-blue-50 p-3 text-blue-600">
                    <FileSpreadsheet size={22} />
                  </div>

                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="truncate font-semibold">
                        {item.arquivo}
                      </p>

                      <span className="text-xs text-slate-400">
                        #{item.id}
                      </span>
                    </div>

                    <div className="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500">
                      <span className="flex items-center gap-1">
                        <CalendarDays size={14} />
                        {dataHora(item.criado_em)}
                      </span>

                      <span className="flex items-center gap-1 text-emerald-600">
                        <CheckCircle2 size={14} />
                        Sucesso
                      </span>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-x-8 gap-y-2 text-sm md:text-right">
                  <div>
                    <p className="text-xs text-slate-400">
                      Faturamento
                    </p>

                    <p className="font-semibold">
                      {moeda(item.indicadores?.faturamento ?? 0)}
                    </p>
                  </div>

                  <div>
                    <p className="text-xs text-slate-400">
                      Vendas
                    </p>

                    <p className="font-semibold">
                      {item.indicadores?.vendas ?? 0}
                    </p>
                  </div>
                </div>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}