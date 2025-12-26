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
  CheckCircle,
  Loader2,
  XCircle,
  MinusCircle,
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

const stepConfig = [
  { id: 'input', label: 'User Input', icon: User },
  { id: 'cache', label: 'Check Cache', icon: Database, isDiamond: true },
  { id: 'researcher', label: 'Researcher', icon: Search },
  { id: 'analyzer', label: 'Analyzer', icon: Brain },
  { id: 'critic', label: 'Critic', icon: MessageSquare },
  { id: 'editor', label: 'Editor', icon: Edit3 },
  { id: 'output', label: 'Output', icon: FileOutput },
]

const mcpServers = [
  { id: 'financials', label: 'Financials' },
  { id: 'valuation', label: 'Valuation' },
  { id: 'volatility', label: 'Volatility' },
  { id: 'macro', label: 'Macro' },
  { id: 'news', label: 'News' },
  { id: 'sentiment', label: 'Sentiment' },
]

function getNodeStatus(
  stepId: string,
  currentStep: string,
  completedSteps: string[],
  cacheHit?: boolean
): NodeStatus {
  if (completedSteps.includes(stepId)) return 'completed'
  if (currentStep === stepId) return 'executing'

  // If cache hit, skip researcher through editor
  if (cacheHit && ['researcher', 'analyzer', 'critic', 'editor'].includes(stepId)) {
    return 'skipped'
  }

  return 'idle'
}

function ProcessNode({
  icon: Icon,
  label,
  status,
  isDiamond = false,
}: {
  icon: React.ElementType
  label: string
  status: NodeStatus
  isDiamond?: boolean
}) {
  const statusStyles = {
    idle: 'bg-gray-700 border-gray-600 opacity-60',
    executing: 'bg-emerald-600 border-emerald-400 shadow-[0_0_12px_rgba(16,185,129,0.6)] animate-pulse',
    completed: 'bg-emerald-700 border-emerald-500 shadow-[0_0_6px_rgba(16,185,129,0.3)]',
    failed: 'bg-red-600 border-red-400 shadow-[0_0_12px_rgba(239,68,68,0.6)]',
    skipped: 'bg-gray-700 border-gray-600 opacity-40 border-dashed',
  }

  const StatusIcon = status === 'completed' ? CheckCircle :
                     status === 'executing' ? Loader2 :
                     status === 'failed' ? XCircle :
                     status === 'skipped' ? MinusCircle : null

  return (
    <div className="flex flex-col items-center gap-1">
      <div
        className={cn(
          'relative flex items-center justify-center w-12 h-12 border-2 transition-all duration-300',
          isDiamond ? 'rotate-45 rounded-md' : 'rounded-lg',
          statusStyles[status]
        )}
      >
        <div className={cn(isDiamond && '-rotate-45')}>
          {StatusIcon && status === 'executing' ? (
            <Loader2 className="w-5 h-5 text-white animate-spin" />
          ) : StatusIcon ? (
            <StatusIcon className="w-5 h-5 text-white" />
          ) : (
            <Icon className="w-5 h-5 text-white" />
          )}
        </div>
      </div>
      <span className={cn(
        'text-xs font-medium transition-opacity duration-300',
        status === 'idle' || status === 'skipped' ? 'text-gray-500' : 'text-gray-300'
      )}>
        {label}
      </span>
      {status === 'skipped' && (
        <span className="text-[10px] text-gray-600">skipped</span>
      )}
    </div>
  )
}

function Connector({ status }: { status: NodeStatus }) {
  return (
    <div className="flex items-center px-1">
      <div
        className={cn(
          'w-6 h-0.5 transition-all duration-300',
          status === 'completed' ? 'bg-emerald-500' :
          status === 'executing' ? 'bg-emerald-400 animate-pulse' :
          status === 'failed' ? 'bg-red-500' :
          'bg-gray-600'
        )}
      />
      <ArrowRight
        className={cn(
          'w-3 h-3 -ml-1 transition-all duration-300',
          status === 'completed' ? 'text-emerald-500' :
          status === 'executing' ? 'text-emerald-400' :
          status === 'failed' ? 'text-red-500' :
          'text-gray-600'
        )}
      />
    </div>
  )
}

function MCPServerGrid({ mcpStatus }: { mcpStatus: MCPStatus }) {
  return (
    <div className="absolute top-16 left-1/2 -translate-x-1/2 bg-gray-800/80 backdrop-blur border border-gray-700 rounded-lg p-3 min-w-[200px]">
      <div className="text-xs text-gray-400 mb-2 text-center">MCP Servers</div>
      <div className="grid grid-cols-3 gap-2">
        {mcpServers.map((server) => {
          const status = mcpStatus[server.id as keyof MCPStatus] || 'idle'
          return (
            <div
              key={server.id}
              className={cn(
                'flex flex-col items-center p-1.5 rounded border transition-all duration-300',
                status === 'completed' ? 'bg-emerald-900/50 border-emerald-600' :
                status === 'executing' ? 'bg-emerald-800/50 border-emerald-500 animate-pulse' :
                status === 'failed' ? 'bg-red-900/50 border-red-600' :
                'bg-gray-800 border-gray-700 opacity-60'
              )}
            >
              <Server className={cn(
                'w-3 h-3 mb-0.5',
                status === 'completed' ? 'text-emerald-400' :
                status === 'executing' ? 'text-emerald-300' :
                status === 'failed' ? 'text-red-400' :
                'text-gray-500'
              )} />
              <span className="text-[9px] text-center leading-tight">
                {server.label}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function LLMNode({ provider, status }: { provider?: string; status: NodeStatus }) {
  return (
    <div className={cn(
      'absolute -bottom-14 left-1/2 -translate-x-1/2 flex flex-col items-center',
      status === 'idle' && 'opacity-60'
    )}>
      <div className="h-4 w-px bg-gray-600" />
      <div className={cn(
        'px-3 py-1.5 rounded-lg border transition-all duration-300',
        status === 'executing' ? 'bg-blue-600 border-blue-400 shadow-[0_0_12px_rgba(59,130,246,0.6)] animate-pulse' :
        status === 'completed' ? 'bg-blue-700 border-blue-500' :
        'bg-gray-800 border-gray-700'
      )}>
        <div className="flex items-center gap-1.5">
          <Brain className={cn(
            'w-3 h-3',
            status === 'executing' || status === 'completed' ? 'text-blue-300' : 'text-gray-500'
          )} />
          <span className="text-xs font-medium text-gray-300">
            {provider || 'LLM'}
          </span>
        </div>
      </div>
    </div>
  )
}

export function ProcessFlow({
  currentStep,
  completedSteps,
  mcpStatus,
  llmProvider,
  cacheHit = false,
}: ProcessFlowProps) {
  // Determine which agent is using LLM
  const llmActiveFor = ['analyzer', 'critic', 'editor'].find(step =>
    currentStep === step || (completedSteps.includes(step) && !completedSteps.includes('output'))
  )
  const llmStatus = llmActiveFor === currentStep ? 'executing' :
                    llmActiveFor ? 'completed' : 'idle'

  return (
    <div className="w-full bg-gray-900/50 border border-gray-800 rounded-xl p-4 overflow-x-auto">
      <div className="text-xs text-gray-500 mb-4 text-center">PROCESS FLOW</div>

      <div className="flex items-start justify-center min-w-[700px] relative pb-20">
        {stepConfig.map((step, index) => {
          const status = getNodeStatus(step.id, currentStep, completedSteps, cacheHit)
          const nextStatus = index < stepConfig.length - 1
            ? getNodeStatus(stepConfig[index + 1].id, currentStep, completedSteps, cacheHit)
            : 'idle'

          return (
            <div key={step.id} className="flex items-start relative">
              <div className="relative">
                <ProcessNode
                  icon={step.icon}
                  label={step.label}
                  status={status}
                  isDiamond={step.isDiamond}
                />

                {/* MCP Servers under Researcher */}
                {step.id === 'researcher' && status !== 'skipped' && (
                  <MCPServerGrid mcpStatus={mcpStatus} />
                )}

                {/* LLM indicator under Analyzer/Critic/Editor cluster */}
                {step.id === 'critic' && (
                  <LLMNode provider={llmProvider} status={llmStatus} />
                )}
              </div>

              {index < stepConfig.length - 1 && (
                <Connector status={
                  status === 'completed' && nextStatus !== 'idle' ? 'completed' :
                  status === 'executing' ? 'executing' :
                  'idle'
                } />
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default ProcessFlow
