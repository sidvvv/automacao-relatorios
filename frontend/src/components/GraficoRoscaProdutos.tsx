
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

type Produto = {
  nome: string
  percentual: number
}

type Props = {
  produtos: Produto[]
}

export const CORES_PRODUTOS = [
  '#2563eb',
  '#10b981',
  '#f59e0b',
  '#8b5cf6',
  '#06b6d4',
  '#f43f5e',
]

export default function GraficoRoscaProdutos({
  produtos,
}: Props) {
  if (produtos.length === 0) {
    return (
      <div className="flex h-full items-center justify-center text-sm text-slate-500">
        Nenhum produto disponível
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie
          data={produtos}
          dataKey="percentual"
          nameKey="nome"
          cx="50%"
          cy="50%"
          innerRadius={58}
          outerRadius={88}
          paddingAngle={2}
          stroke="#ffffff"
          strokeWidth={2}
        >
          {produtos.map((produto, index) => (
            <Cell
              key={produto.nome}
              fill={
                CORES_PRODUTOS[
                  index % CORES_PRODUTOS.length
                ]
              }
            />
          ))}
        </Pie>

        <Tooltip
          formatter={(valor) =>
            `${Number(valor ?? 0).toLocaleString('pt-BR', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}%`
          }
          contentStyle={{
            borderRadius: 12,
            border: '1px solid #e2e8f0',
            backgroundColor: '#ffffff',
          }}
        />
      </PieChart>
    </ResponsiveContainer>
  )
}
