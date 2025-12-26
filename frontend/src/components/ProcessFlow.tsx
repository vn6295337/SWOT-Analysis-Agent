import { cn } from "@/lib/utils"
import {
  User,
  Database,
  Search,
  Brain,
  MessageSquare,
  Edit3,
  FileOutput,
  Server,
  ArrowRight,
  ArrowDown,
  CheckCircle,
  Loader2,
  XCircle,
  MinusCircle,
  Network,
  GitBranch,
} from "lucide-react"
import type { MCPStatus } from "@/lib/api"

type NodeStatus = 'idle' | 'executing' | 'completed' | 'failed' | 'skipped'

interface ProcessFlowProps {
  currentStep: string
  completedSteps: string[]
  mcpStatus: MCPStatus
  llmProvider?: string
  cacheHit?: boolean
}

const mcpServers = [
  { id: 'financials', label: 'Fin' },
  { id: 'valuation', label: 'Val' },
  { id: 'volatility', label: 'Vol' },
  { id: 'macro', label: 'Mac' },
  { id: 'news', label: 'News' },
  { id: 'sentiment', label: 'Sent' },
]

function getNodeStatus(
  stepId: string,
  currentStep: string,
  completedSteps: string[],
  cacheHit?: boolean
): NodeStatus {
  if (completedSteps.includes(stepId)) return 'completed'
  if (currentStep === stepId) return 'executing'
  if (cacheHit && ['researcher', 'analyzer', 'critic', 'editor'].includes(stepId)) {
    return 'skipped'
  }
  return 'idle'
}

const statusStyles = {
  idle: 'bg-gray-700 border-gray-600',
  executing: 'bg-emerald-600 border-emerald-400 shadow-[0_0_12px_rgba(16,185,129,0.5)] animate-pulse',
  completed: 'bg-emerald-700 border-emerald-500',
  failed: 'bg-red-600 border-red-400',
  skipped: 'bg-gray-700 border-gray-600 opacity-40 border-dashed',
}

const connectorColor = (status: NodeStatus) =>
  status === 'completed' ? 'bg-emerald-500' :
  status === 'executing' ? 'bg-emerald-400' :
  'bg-gray-600'

const arrowColor = (status: NodeStatus) =>
  status === 'completed' ? 'text-emerald-500' :
  status === 'executing' ? 'text-emerald-400' :
  'text-gray-600'

// === COMPONENTS ===

function ProcessNode({
  icon: Icon,
  label,
  status,
  isDiamond = false,
  size = 'normal',
}: {
  icon: React.ElementType
  label: string
  status: NodeStatus
  isDiamond?: boolean
  size?: 'normal' | 'small'
}) {
  const StatusIcon = status === 'completed' ? CheckCircle :
                     status === 'executing' ? Loader2 :
                     status === 'failed' ? XCircle :
                     status === 'skipped' ? MinusCircle : null

  const nodeSize = size === 'small' ? 'w-9 h-9' : 'w-11 h-11'
  const iconSize = size === 'small' ? 'w-4 h-4' : 'w-5 h-5'

  return (
    <div className="flex flex-col items-center gap-1">
      <div
        className={cn(
          'flex items-center justify-center border-2 transition-all duration-300',
          nodeSize,
          isDiamond ? 'rotate-45 rounded-md' : 'rounded-lg',
          statusStyles[status],
          status === 'idle' && 'opacity-50'
        )}
      >
        <div className={cn(isDiamond && '-rotate-45')}>
          {StatusIcon && status === 'executing' ? (
            <Loader2 className={cn(iconSize, 'text-white animate-spin')} />
          ) : StatusIcon ? (
            <StatusIcon className={cn(iconSize, 'text-white')} />
          ) : (
            <Icon className={cn(iconSize, 'text-white')} />
          )}
        </div>
      </div>
      <span className={cn(
        'text-[10px] font-medium text-center leading-tight',
        status === 'idle' || status === 'skipped' ? 'text-gray-500' : 'text-gray-300'
      )}>
        {label}
      </span>
    </div>
  )
}

function HArrow({ status }: { status: NodeStatus }) {
  return (
    <div className="flex items-center justify-center w-6">
      <div className={cn('w-3 h-0.5', connectorColor(status))} />
      <ArrowRight className={cn('w-3 h-3 -ml-0.5', arrowColor(status))} />
    </div>
  )
}

function VLine({ status, className }: { status: NodeStatus; className?: string }) {
  return (
    <div className={cn('w-0.5 bg-gray-600', connectorColor(status), className)} />
  )
}

function VArrow({ status }: { status: NodeStatus }) {
  return (
    <div className="flex flex-col items-center">
      <VLine status={status} className="h-4" />
      <ArrowDown className={cn('w-3 h-3 -mt-0.5', arrowColor(status))} />
    </div>
  )
}

function MCPServer({ id, label, status }: { id: string; label: string; status: NodeStatus }) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center p-1 rounded border transition-all duration-300 w-10 h-10',
        status === 'completed' ? 'bg-emerald-900/50 border-emerald-600' :
        status === 'executing' ? 'bg-emerald-800/50 border-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]' :
        'bg-gray-800 border-gray-700 opacity-50'
      )}
    >
      <Server className={cn(
        'w-3 h-3',
        status === 'completed' ? 'text-emerald-400' :
        status === 'executing' ? 'text-emerald-300' :
        'text-gray-500'
      )} />
      <span className="text-[8px] text-gray-400 mt-0.5">{label}</span>
    </div>
  )
}

function LLMBox({ provider, status }: { provider?: string; status: NodeStatus }) {
  return (
    <div className={cn(
      'flex items-center gap-1.5 px-2 py-1 rounded border transition-all duration-300',
      status === 'executing' ? 'bg-blue-600 border-blue-400 shadow-[0_0_10px_rgba(59,130,246,0.5)] animate-pulse' :
      status === 'completed' ? 'bg-blue-700 border-blue-500' :
      'bg-gray-800 border-gray-700 opacity-50'
    )}>
      <Brain className={cn(
        'w-3 h-3',
        status === 'executing' || status === 'completed' ? 'text-blue-300' : 'text-gray-500'
      )} />
      <span className="text-[10px] font-medium text-gray-300">{provider || 'LLM'}</span>
    </div>
  )
}

// === MAIN COMPONENT ===

export function ProcessFlow({
  currentStep,
  completedSteps,
  mcpStatus,
  llmProvider,
  cacheHit = false,
}: ProcessFlowProps) {
  // Statuses
  const inputStatus = getNodeStatus('input', currentStep, completedSteps, cacheHit)
  const cacheStatus = getNodeStatus('cache', currentStep, completedSteps, cacheHit)
  const a2aStatus = getNodeStatus('a2a_client', currentStep, completedSteps, cacheHit)
  const analyzerStatus = getNodeStatus('analyzer', currentStep, completedSteps, cacheHit)
  const criticStatus = getNodeStatus('critic', currentStep, completedSteps, cacheHit)
  const editorStatus = getNodeStatus('editor', currentStep, completedSteps, cacheHit)
  const outputStatus = getNodeStatus('output', currentStep, completedSteps, cacheHit)
  const researcherStatus = getNodeStatus('researcher', currentStep, completedSteps, cacheHit)
  const exchangeStatus = getNodeStatus('exchange_match', currentStep, completedSteps, cacheHit)

  const llmActive = ['analyzer', 'critic', 'editor'].find(s =>
    currentStep === s || (completedSteps.includes(s) && !completedSteps.includes('output'))
  )
  const llmStatus: NodeStatus = llmActive === currentStep ? 'executing' : llmActive ? 'completed' : 'idle'

  const conn = (from: NodeStatus, to: NodeStatus): NodeStatus =>
    from === 'completed' && to !== 'idle' ? 'completed' :
    from === 'executing' ? 'executing' : 'idle'

  return (
    <div className="w-full p-4 overflow-x-auto">
      {/*
        Grid layout:
        Row 1: Input | Cache | A2A | [Analyzer-Critic-Editor] | Output
        Row 2: Exchange |  -  | Researcher + MCP Servers |  -  |  -
        Row 3:    -    |  -  |      -      | LLM |  -
      */}
      <div className="grid grid-cols-[auto_auto_auto_1fr_auto] grid-rows-[auto_auto_auto] gap-x-2 gap-y-3 justify-items-center items-start min-w-[700px]">

        {/* === ROW 1 === */}

        {/* R1C1: User Input */}
        <div className="flex items-center">
          <ProcessNode icon={User} label="User Input" status={inputStatus} />
          <HArrow status={conn(inputStatus, cacheStatus)} />
        </div>

        {/* R1C2: Cache */}
        <div className="flex items-center">
          <ProcessNode icon={Database} label="Cache" status={cacheStatus} isDiamond />
          <HArrow status={conn(cacheStatus, a2aStatus)} />
        </div>

        {/* R1C3: A2A Client */}
        <div className="flex items-center">
          <ProcessNode icon={Network} label="A2A Client" status={a2aStatus} />
          <HArrow status={conn(a2aStatus, analyzerStatus)} />
        </div>

        {/* R1C4: Analyzer → Critic → Editor (grouped) */}
        <div className="flex items-center">
          <div className="border border-dashed border-gray-600 rounded-lg px-3 py-2">
            <div className="text-[9px] text-gray-500 text-center mb-1">LLM Agents</div>
            <div className="flex items-center gap-1">
              <ProcessNode icon={Brain} label="Analyzer" status={analyzerStatus} size="small" />
              <HArrow status={conn(analyzerStatus, criticStatus)} />
              <ProcessNode icon={MessageSquare} label="Critic" status={criticStatus} size="small" />
              <HArrow status={conn(criticStatus, editorStatus)} />
              <ProcessNode icon={Edit3} label="Editor" status={editorStatus} size="small" />
            </div>
          </div>
          <HArrow status={conn(editorStatus, outputStatus)} />
        </div>

        {/* R1C5: Output */}
        <ProcessNode icon={FileOutput} label="Output" status={outputStatus} />

        {/* === ROW 2 === */}

        {/* R2C1: Vertical connector + Exchange Match */}
        <div className="flex flex-col items-center">
          <VArrow status={conn(inputStatus, exchangeStatus)} />
          <ProcessNode icon={GitBranch} label="Exchange" status={exchangeStatus} />
        </div>

        {/* R2C2: Empty */}
        <div />

        {/* R2C3: Vertical connector + Researcher + MCP Servers */}
        <div className="flex flex-col items-center col-span-1">
          <VArrow status={conn(a2aStatus, researcherStatus)} />
          <div className="flex items-center gap-2">
            <ProcessNode icon={Search} label="Researcher" status={researcherStatus} />
            <div className={cn('w-3 h-0.5', connectorColor(researcherStatus))} />
            <div className="flex gap-1 p-1.5 bg-gray-800/50 border border-gray-700 rounded-lg">
              {mcpServers.map((s) => (
                <MCPServer
                  key={s.id}
                  id={s.id}
                  label={s.label}
                  status={mcpStatus[s.id as keyof MCPStatus] || 'idle'}
                />
              ))}
            </div>
          </div>
        </div>

        {/* R2C4: Empty */}
        <div />

        {/* R2C5: Empty */}
        <div />

        {/* === ROW 3 === */}

        {/* R3C1-3: Empty */}
        <div />
        <div />
        <div />

        {/* R3C4: LLM (centered under agents) */}
        <div className="flex flex-col items-center">
          <VLine status={llmStatus} className="h-3" />
          <LLMBox provider={llmProvider} status={llmStatus} />
        </div>

        {/* R3C5: Empty */}
        <div />
      </div>
    </div>
  )
}

export default ProcessFlow
