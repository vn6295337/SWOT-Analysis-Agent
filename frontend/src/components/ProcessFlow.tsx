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
  const nodeSize = size === 'small' ? 'w-9 h-9' : 'w-11 h-11'
  const iconSize = size === 'small' ? 'w-4 h-4' : 'w-5 h-5'

  // Show spinner only when executing, otherwise show original icon
  const showSpinner = status === 'executing'

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
          {showSpinner ? (
            <Loader2 className={cn(iconSize, 'text-white animate-spin')} />
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

function HDash({ status }: { status: NodeStatus }) {
  return (
    <div className="flex items-center justify-center w-6 h-11">
      <div className={cn('w-full h-0.5', connectorColor(status))} />
    </div>
  )
}

function VDash({ status }: { status: NodeStatus }) {
  return (
    <div className="flex justify-center w-11 h-4">
      <div className={cn('w-0.5 h-full', connectorColor(status))} />
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

  const conn = (from: NodeStatus, to: NodeStatus): NodeStatus =>
    from === 'completed' && to !== 'idle' ? 'completed' :
    from === 'executing' ? 'executing' : 'idle'

  return (
    <div className="w-full p-4 overflow-x-auto">
      <div className="min-w-[800px]">
        {/* Row 1: Main flow - evenly spaced */}
        <div className="flex items-center justify-between">
          <ProcessNode icon={User} label="User Input" status={inputStatus} />
          <HDash status={conn(inputStatus, cacheStatus)} />
          <ProcessNode icon={Database} label="Cache" status={cacheStatus} isDiamond />
          <HDash status={conn(cacheStatus, a2aStatus)} />
          <ProcessNode icon={Network} label="A2A Client" status={a2aStatus} />
          <HDash status={conn(a2aStatus, analyzerStatus)} />
          <ProcessNode icon={Brain} label="Analyzer" status={analyzerStatus} />
          <HDash status={conn(analyzerStatus, criticStatus)} />
          <ProcessNode icon={MessageSquare} label="Critic" status={criticStatus} />
          <HDash status={conn(criticStatus, editorStatus)} />
          <ProcessNode icon={Edit3} label="Editor" status={editorStatus} />
          <HDash status={conn(editorStatus, outputStatus)} />
          <ProcessNode icon={FileOutput} label="Output" status={outputStatus} />
        </div>

        {/* Row 2: Exchange (under User Input) and Researcher (under A2A) */}
        <div className="flex mt-1">
          {/* Exchange - aligned under User Input */}
          <div className="flex flex-col items-center" style={{ width: '44px' }}>
            <VDash status={conn(inputStatus, exchangeStatus)} />
            <ProcessNode icon={GitBranch} label="Exchange" status={exchangeStatus} />
          </div>

          {/* Spacer to align Researcher under A2A (skip Cache) */}
          <div className="flex-1" style={{ maxWidth: '140px' }} />

          {/* Researcher + MCP - aligned under A2A */}
          <div className="flex flex-col items-center">
            <VDash status={conn(a2aStatus, researcherStatus)} />
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
        </div>
      </div>
    </div>
  )
}

export default ProcessFlow
