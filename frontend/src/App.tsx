import { useState } from 'react'

import {
  LayoutDashboard,
  FileUp,
  History,
  Settings,
  ChartNoAxesCombined,
  Wallet,
  ShoppingCart,
  Receipt,
  Users,
  CheckCircle2,
} from 'lucide-react'

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts'

const indicadores = [
  {
    titulo: 'Faturamento',
    valor: 'R$ 426.074,60',
    Icon: Wallet,
  },
  {
    titulo: 'Vendas',
    valor: '1.200',
    Icon: ShoppingCart,
  },
  {
    titulo: 'Ticket médio',
    valor: 'R$ 355,06',
    Icon: Receipt,
  },
  {
    titulo: 'Clientes únicos',
    valor: '80',
    Icon: Users,
  },
]

const produtos = [
  { nome: 'Jaqueta', percentual: 36.54 },
  { nome: 'Tênis', percentual: 30.19 },
  { nome: 'Calça jeans', percentual: 17.74 },
  { nome: 'Camiseta', percentual: 7.58 },
  { nome: 'Boné', percentual: 5.89 },
  { nome: 'Meia', percentual: 2.06 },
]

const meses = [
  { nome: 'Jan', valor: 41519.7 },
  { nome: 'Fev', valor: 46217.6 },
  { nome: 'Mar', valor: 43352.2 },
  { nome: 'Abr', valor: 46981.1 },
  { nome: 'Mai', valor: 46693.3 },
  { nome: 'Jun', valor: 42613.8 },
  { nome: 'Jul', valor: 48695.7 },
  { nome: 'Ago', valor: 43391.3 },
  { nome: 'Set', valor: 43536.8 },
  { nome: 'Out*', valor: 23073.1 },
]



type RespostaAPI = {
  arquivo: string

  periodo: {
    inicio: string
    fim: string
  }

  indicadores: {
    faturamento: number
    vendas: number
    ticket_medio: number
    clientes_unicos: number
  }

  faturamento_mensal: {
    mes: string
    faturamento: number
  }[]

  ranking_produtos: {
    produto: string
    faturamento: number
    participacao: number
  }[]

  resumo_limpeza: {
    linhas_lidas: number
    duplicadas_removidas: number
    campos_corrigidos: number
  }
}


function App() {
  
const [arquivo, setArquivo] = useState<File | null>(null)
const [resultado, setResultado] = useState<RespostaAPI | null>(null)
const [carregando, setCarregando] = useState(false)
const [erro, setErro] = useState('')

async function enviarArquivo() {
  if (!arquivo) return

  if (arquivo.size > 10 * 1024 * 1024) {
    setErro('O arquivo deve ter no máximo 10 MB.')
    return
  }

  const formulario = new FormData()
  formulario.append('arquivo', arquivo)

  setCarregando(true)
  setErro('')
  setResultado(null)

  try {
    const resposta = await fetch('/api/relatorios/processar', {
      method: 'POST',
      body: formulario,
    })

    const dados = await resposta.json()

    if (!resposta.ok) {
      throw new Error(
        typeof dados.detail === 'string'
          ? dados.detail
          : 'Não foi possível processar o arquivo.'
      )
    }

    setResultado(dados as RespostaAPI)
  } catch (error) {
    setErro(
      error instanceof Error
        ? error.message
        : 'Erro inesperado na comunicação com o servidor.'
    )
  } finally {
    setCarregando(false)
  }
}

  
const formatarMoeda = (valor: number) =>
  new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(valor)

const formatarData = (data: string) => {
  const [ano, mes, dia] = data.split('-')
  return `${dia}/${mes}/${ano}`
}

// Indicadores reais após o upload
const indicadoresExibidos = resultado
  ? [
      {
        titulo: 'Faturamento',
        valor: formatarMoeda(resultado.indicadores.faturamento),
        Icon: Wallet,
      },
      {
        titulo: 'Vendas',
        valor: resultado.indicadores.vendas.toLocaleString('pt-BR'),
        Icon: ShoppingCart,
      },
      {
        titulo: 'Ticket médio',
        valor: formatarMoeda(resultado.indicadores.ticket_medio),
        Icon: Receipt,
      },
      {
        titulo: 'Clientes únicos',
        valor: resultado.indicadores.clientes_unicos.toLocaleString('pt-BR'),
        Icon: Users,
      },
    ]
  : indicadores

// Faturamento mensal real
const mesesExibidos = resultado
  ? resultado.faturamento_mensal.map((item) => {
      const [ano, numeroMes] = item.mes.split('-').map(Number)

      const nomeMes = new Date(ano, numeroMes - 1, 1)
        .toLocaleDateString('pt-BR', { month: 'short' })
        .replace('.', '')

      const ultimoDia = new Date(ano, numeroMes, 0).getDate()
      const fimPeriodo = resultado.periodo.fim

      const parcial =
        item.mes === fimPeriodo.slice(0, 7) &&
        Number(fimPeriodo.slice(8, 10)) < ultimoDia

      return {
        nome: `${nomeMes}${parcial ? '*' : ''}`,
        valor: item.faturamento,
      }
    })
  : meses

// Participação real por produto
const produtosExibidos = resultado
  ? resultado.ranking_produtos.map((item) => ({
      nome: item.produto,
      percentual: item.participacao,
    }))
  : produtos

const periodoExibido = resultado
  ? `${formatarData(resultado.periodo.inicio)} a ${formatarData(resultado.periodo.fim)}`
  : '01/01/2026 a 16/10/2026'

const resumoExibido = resultado
  ? resultado.resumo_limpeza
  : {
      linhas_lidas: 1237,
      duplicadas_removidas: 37,
      campos_corrigidos: 42,
    }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="flex min-h-screen">

        {/* Menu lateral */}
        <aside className="hidden w-64 shrink-0 bg-slate-950 px-5 py-8 text-white lg:block">
          <div className="mb-12 flex items-center gap-3">
            <div className="rounded-xl bg-blue-600 p-2">
              <ChartNoAxesCombined size={24} />
            </div>
            <div>
              <h2 className="text-lg font-bold">DataFlow</h2>
              <p className="text-xs text-slate-400">Analytics</p>
            </div>
          </div>

          <nav className="space-y-2 text-sm">
            <div className="flex items-center gap-3 rounded-xl bg-blue-600 px-4 py-3 font-medium">
              <LayoutDashboard size={19} />
              Dashboard
            </div>

            <div className="flex items-center gap-3 px-4 py-3 text-slate-400">
              <FileUp size={19} />
              Importar dados
            </div>

            <div className="flex items-center gap-3 px-4 py-3 text-slate-400">
              <History size={19} />
              Histórico
            </div>

            <div className="flex items-center gap-3 px-4 py-3 text-slate-400">
              <Settings size={19} />
              Configurações
            </div>
          </nav>
        </aside>

        {/* Conteúdo principal */}
        <main className="min-w-0 flex-1 px-5 py-8 md:px-10">
          <div className="mx-auto max-w-7xl">


        <header className="mb-8">
          <p className="mb-1 text-sm font-medium text-blue-600">
            Visão geral
          </p>

          <h1 className="text-3xl font-bold tracking-tight">
            Dashboard de Vendas
          </h1>

          <p className="mt-2 text-sm text-slate-500">
            Período: {periodoExibido}
          </p>

          {!resultado && (
            <p className="mt-2 text-xs text-amber-600">
              Dados de demonstração. Importe uma planilha para
              visualizar os resultados reais.
            </p>
          )}
        </header>

            
<section className="mb-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
  <h3 className="text-lg font-semibold">Importar planilha</h3>

  <p className="mt-1 text-sm text-slate-500">
    Envie os dados de vendas para processamento automático.
  </p>

  <div className="mt-5 flex flex-col gap-3 sm:flex-row">
    <input
      type="file"
      accept=".csv,.xlsx"
      onChange={(e) => {
        setArquivo(e.target.files?.[0] ?? null)
        setResultado(null)
        setErro('')
      }}
      className="min-w-0 flex-1 rounded-xl border border-slate-200 p-3 text-sm"
    />

    <button
      type="button"
      onClick={enviarArquivo}
      disabled={!arquivo || carregando}
      className="rounded-xl bg-blue-600 px-6 py-3 font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
    >
      {carregando ? 'Processando...' : 'Processar planilha'}
    </button>
  </div>

  {erro && (
    <p role="alert" className="mt-4 text-sm text-red-600">
      {erro}
    </p>
  )}

  {resultado && (
    <div className="mt-5 rounded-xl bg-emerald-50 p-4">
      <p className="font-medium text-emerald-800">
        Planilha processada com sucesso!
      </p>

      <p className="mt-2 text-sm text-emerald-900">
        Arquivo: {resultado.arquivo}
      </p>

      <p className="text-sm text-emerald-900">
        Faturamento: {resultado.indicadores.faturamento.toLocaleString(
          'pt-BR',
          { style: 'currency', currency: 'BRL' }
        )}
      </p>

      <p className="text-sm text-emerald-900">
        Vendas: {resultado.indicadores.vendas}
      </p>

      <p className="text-sm text-emerald-900">
        Clientes únicos: {resultado.indicadores.clientes_unicos}
      </p>
    </div>
  )}
</section>


            {/* Indicadores */}
            <section className="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-4">
              {indicadoresExibidos.map(({ titulo, valor, Icon }) => (
                <div
                  key={titulo}
                  className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
                >
                  <div className="mb-4 flex items-center justify-between">
                    <span className="text-sm text-slate-500">
                      {titulo}
                    </span>
                    <div className="rounded-lg bg-blue-50 p-2 text-blue-600">
                      <Icon size={20} />
                    </div>
                  </div>
                  <h2 className="text-2xl font-bold tracking-tight">
                    {valor}
                  </h2>
                </div>
              ))}
            </section>

            {/* Gráficos */}
            <section className="mt-6 grid grid-cols-1 gap-6 xl:grid-cols-2">

              <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <h3 className="font-semibold">Faturamento mensal</h3>
                <p className="mt-1 text-sm text-slate-500">
                  Evolução das vendas em 2026
                </p>

                
<div className="mt-6 h-72 w-full">
  <ResponsiveContainer width="100%" height="100%">
    <LineChart
      data={mesesExibidos}
      margin={{
        top: 15,
        right: 20,
        left: 15,
        bottom: 20,
      }}
    >
        <CartesianGrid
      strokeDasharray="3 3"
      vertical={false}
      stroke="#e2e8f0"
    />

  
      <XAxis
        dataKey="nome"
        tickLine={false}
        axisLine={false}
        tickMargin={15}
        height={45}
        tick={{
          fontSize: 14,
          fill: '#475569',
        }}
      />


    

      <YAxis
        width={95}
        tickLine={false}
        axisLine={false}
        tickMargin={14}
        tick={{ fontSize: 14, fill: '#475569' }}
        tickFormatter={(valor: number) => {
          if (Math.abs(valor) >= 1000) {
            return `${(valor / 1000).toLocaleString('pt-BR', {
              maximumFractionDigits: 1,
            })} mil`
          }

          return `R$ ${valor.toLocaleString('pt-BR', {
            maximumFractionDigits: 0,
          })}`
        }}
      />



      <Tooltip
        formatter={(valor) =>
          `R$ ${Number(valor ?? 0).toLocaleString(
            'pt-BR',
            {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            }
          )}`
        }
      />

      <Line
        type="monotone"
        dataKey="valor"
        name="Faturamento"
        stroke="#2563eb"
        strokeWidth={3}
        dot={{ r: 4, fill: '#2563eb' }}
        activeDot={{ r: 6 }}
      />
    </LineChart>
  </ResponsiveContainer>
</div>
  {/* Aviso sobre o mês parcial */}
  {mesesExibidos.some((mes) => mes.nome.endsWith('*')) && (
    <p className="mt-3 text-xs text-slate-400">
      * Último mês com dados parciais.
    </p>
  )}

                <p className="mt-2 text-sm text-slate-500">
                  Período: {periodoExibido}
                </p>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <h3 className="font-semibold">Participação por produto</h3>
                <p className="mt-1 text-sm text-slate-500">
                  Distribuição do faturamento
                </p>

                <div className="mt-7 space-y-4">
                  {produtosExibidos.map((produto) => (
                    <div key={produto.nome}>
                      <div className="mb-1.5 flex justify-between text-sm">
                        <span>{produto.nome}</span>
                        <span className="text-slate-500">
                          {produto.percentual.toFixed(2)}%
                        </span>
                      </div>

                      <div className="h-2.5 overflow-hidden rounded-full bg-slate-100">
                        <div
                          className="h-full rounded-full bg-blue-600"
                          style={{
                            width: `${produto.percentual}%`,
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

            </section>

            {/* Qualidade dos dados */}
            <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="font-semibold">Qualidade dos dados</h3>

              <div className="mt-4 flex items-center gap-3">
                <CheckCircle2 className="text-emerald-600" size={22} />
                <span className="text-sm text-slate-600">
                  {resumoExibido.linhas_lidas.toLocaleString('pt-BR')} registros
                  analisados · {resumoExibido.duplicadas_removidas} duplicatas
                  removidas · {resumoExibido.campos_corrigidos} campos corrigidos
                </span>
              </div>
            </section>

          </div>
        </main>
      </div>
    </div>
  )
}

export default App
