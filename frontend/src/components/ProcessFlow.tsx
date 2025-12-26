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
  Network,
  GitBranch,
} from "lucide-react"
import type { MCPStatus } from "@/lib/api"

type NodeStatus = 'idle' | 'executing' | 'completed' | 'failed' | 'skipped'
type CacheState = 'idle' | 'hit' | 'miss' | 'checking'

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
  if (cacheHit && ['researcher', 'analyzer', 'critic', 'editor', 'a2a_client'].includes(stepId)) {
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

const cacheStyles = {
  idle: 'bg-gray-700 border-gray-600',
  checking: 'bg-emerald-600 border-emerald-400 shadow-[0_0_12px_rgba(16,185,129,0.5)] animate-pulse',
  hit: 'bg-emerald-700 border-emerald-500',
  miss: 'bg-amber-600 border-amber-500',
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
  cacheState,
}: {
  icon: React.ElementType
  label: string
  status: NodeStatus
  isDiamond?: boolean
  cacheState?: CacheState
}) {
  const showSpinner = status === 'executing' || cacheState === 'checking'

  // Use cache-specific styles if cacheState is provided
  const boxStyle = cacheState
    ? cacheStyles[cacheState]
    : statusStyles[status]

  return (
    <div className="flex flex-col items-center gap-1">
      <div
        className={cn(
          'flex items-center justify-center border-2 transition-all duration-300 w-11 h-11',
          isDiamond ? 'rotate-45 rounded-md' : 'rounded-lg',
          boxStyle,
          status === 'idle' && !cacheState && 'opacity-50'
        )}
      >
        <div className={cn(isDiamond && '-rotate-45')}>
          {showSpinner ? (
            <Loader2 className="w-5 h-5 text-white animate-spin" />
          ) : (
            <Icon className="w-5 h-5 text-white" />
          )}
        </div>
      </div>
      <span className={cn(
        'text-[10px] font-medium text-center leading-tight whitespace-nowrap',
        status === 'idle' || status === 'skipped' ? 'text-gray-500' : 'text-gray-300'
      )}>
        {label}
      </span>
    </div>
  )
}

function HDash({ status }: { status: NodeStatus }) {
  return (
    <div className="flex items-center justify-center w-8">
      <div className={cn('w-full h-0.5', connectorColor(status))} />
    </div>
  )
}

function VDash({ status, height = 'h-4' }: { status: NodeStatus; height?: string }) {
  return (
    <div className={cn('flex justify-center w-11', height)}>
      <div className={cn('w-0.5 h-full', connectorColor(status))} />
    </div>
  )
}

function LLMProvider({ name, status }: { name: string; status: NodeStatus }) {
  return (
    <div
      className={cn(
        'flex items-center justify-center px-2 py-1.5 rounded border transition-all duration-300',
        status === 'completed' ? 'bg-blue-900/50 border-blue-600' :
        status === 'executing' ? 'bg-blue-800/50 border-blue-500 animate-pulse shadow-[0_0_8px_rgba(59,130,246,0.5)]' :
        'bg-gray-800 border-gray-700 opacity-50'
      )}
    >
      <span className={cn(
        'text-[9px] font-medium',
        status === 'completed' ? 'text-blue-300' :
        status === 'executing' ? 'text-blue-200' :
        'text-gray-500'
      )}>{name}</span>
    </div>
  )
}

function MCPServer({ label, status }: { label: string; status: NodeStatus }) {
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
  cacheHit = false,
}: ProcessFlowProps) {
  // Statuses
  const inputStatus = getNodeStatus('input', currentStep, completedSteps, cacheHit)
  const a2aStatus = getNodeStatus('a2a_client', currentStep, completedSteps, cacheHit)
  const analyzerStatus = getNodeStatus('analyzer', currentStep, completedSteps, cacheHit)
  const criticStatus = getNodeStatus('critic', currentStep, completedSteps, cacheHit)
  const editorStatus = getNodeStatus('editor', currentStep, completedSteps, cacheHit)
  const outputStatus = getNodeStatus('output', currentStep, completedSteps, cacheHit)
  const researcherStatus = getNodeStatus('researcher', currentStep, completedSteps, cacheHit)
  const exchangeStatus = getNodeStatus('exchange_match', currentStep, completedSteps, cacheHit)

  // Cache state: idle, checking, hit, or miss
  const cacheState: CacheState =
    currentStep === 'cache' ? 'checking' :
    completedSteps.includes('cache') ? (cacheHit ? 'hit' : 'miss') :
    'idle'

  // LLM status - active when any of analyzer/critic/editor is running
  const llmActive = ['analyzer', 'critic', 'editor'].some(s =>
    currentStep === s || completedSteps.includes(s)
  )
  const llmStatus: NodeStatus = ['analyzer', 'critic', 'editor'].some(s => currentStep === s)
    ? 'executing'
    : llmActive ? 'completed' : 'idle'

  const conn = (from: NodeStatus, to: NodeStatus): NodeStatus =>
    from === 'completed' && to !== 'idle' ? 'completed' :
    from === 'executing' ? 'executing' : 'idle'

  // Bypass connector status (for cache hit path)
  const bypassStatus: NodeStatus = cacheHit && completedSteps.includes('cache') ? 'completed' : 'idle'

  return (
    <div className="w-full p-4 overflow-x-auto">
      <div className="min-w-[900px] relative">

        {/* Cache bypass elbow (above Row 1) */}
        <div className="absolute top-0 left-0 right-0 h-6 pointer-events-none">
          {/* Horizontal line at top */}
          <div
            className={cn(
              'absolute h-0.5 transition-all duration-300',
              bypassStatus === 'completed' ? 'bg-emerald-500' : 'bg-gray-700'
            )}
            style={{ left: '85px', right: '30px', top: '2px' }}
          />
          {/* Left vertical (from cache up) */}
          <div
            className={cn(
              'absolute w-0.5 transition-all duration-300',
              bypassStatus === 'completed' ? 'bg-emerald-500' : 'bg-gray-700'
            )}
            style={{ left: '85px', top: '2px', height: '20px' }}
          />
          {/* Right vertical (down to output) */}
          <div
            className={cn(
              'absolute w-0.5 transition-all duration-300',
              bypassStatus === 'completed' ? 'bg-emerald-500' : 'bg-gray-700'
            )}
            style={{ right: '30px', top: '2px', height: '20px' }}
          />
        </div>

        {/* Row 1: Main flow */}
        <div className="flex items-start justify-between pt-6">
          <ProcessNode icon={User} label="User Input" status={inputStatus} />
          <HDash status={conn(inputStatus, cacheState === 'idle' ? 'idle' : 'completed')} />
          <ProcessNode icon={Database} label="Cache" status={cacheState === 'idle' ? 'idle' : 'completed'} isDiamond cacheState={cacheState} />
          <HDash status={cacheState === 'miss' ? conn('completed' as NodeStatus, a2aStatus) : 'idle'} />
          <ProcessNode icon={Network} label="A2A Client" status={a2aStatus} />
          <HDash status={conn(a2aStatus, analyzerStatus)} />

          {/* Grouped: Analyzer, Critic, Editor */}
          <div className="flex gap-0.5 p-1 border border-gray-700 rounded-lg bg-gray-800/30">
            <ProcessNode icon={Brain} label="Analyzer" status={analyzerStatus} />
            <HDash status={conn(analyzerStatus, criticStatus)} />
            <ProcessNode icon={MessageSquare} label="Critic" status={criticStatus} />
            <HDash status={conn(criticStatus, editorStatus)} />
            <ProcessNode icon={Edit3} label="Editor" status={editorStatus} />
          </div>

          <HDash status={conn(editorStatus, outputStatus)} />
          <ProcessNode icon={FileOutput} label="Output" status={outputStatus} />
        </div>

        {/* Row 2: Exchange + LLM Providers */}
        <div className="flex items-start mt-1">
          {/* Exchange under User Input */}
          <div className="flex flex-col items-center" style={{ width: '44px' }}>
            <VDash status={conn(inputStatus, exchangeStatus)} />
            <ProcessNode icon={GitBranch} label="Exchange" status={exchangeStatus} />
          </div>

          {/* Spacer */}
          <div className="flex-1" />

          {/* Grouped: LLM Providers under agents */}
          <div className="flex gap-0.5 p-1 border border-gray-700 rounded-lg bg-gray-800/30">
            <div className="flex flex-col items-center gap-1">
              <VDash status={llmStatus} height="h-3" />
              <LLMProvider name="Groq" status={llmStatus} />
            </div>
            <div className="w-8" /> {/* spacer matching HDash */}
            <div className="flex flex-col items-center gap-1">
              <VDash status={llmStatus} height="h-3" />
              <LLMProvider name="Gemini" status={llmStatus} />
            </div>
            <div className="w-8" /> {/* spacer matching HDash */}
            <div className="flex flex-col items-center gap-1">
              <VDash status={llmStatus} height="h-3" />
              <LLMProvider name="OpenRouter" status={llmStatus} />
            </div>
          </div>

          {/* Spacer for Output column */}
          <div style={{ width: '80px' }} />
        </div>

        {/* Row 3: Researcher + MCP Servers */}
        <div className="flex items-start mt-3">
          {/* Researcher in first column */}
          <ProcessNode icon={Search} label="Researcher" status={researcherStatus} />

          <HDash status={researcherStatus} />

          {/* Grouped: MCP Servers */}
          <div className="flex gap-1 p-1.5 border border-gray-700 rounded-lg bg-gray-800/30">
            {mcpServers.map((s) => (
              <MCPServer
                key={s.id}
                label={s.label}
                status={mcpStatus[s.id as keyof MCPStatus] || 'idle'}
              />
            ))}
          </div>
        </div>

        {/* A2A to Researcher elbow connector */}
        <div className="absolute pointer-events-none" style={{ top: '90px', left: '195px' }}>
          {/* Vertical down from A2A */}
          <div
            className={cn(
              'absolute w-0.5 transition-all duration-300',
              conn(a2aStatus, researcherStatus) === 'completed' ? 'bg-emerald-500' :
              conn(a2aStatus, researcherStatus) === 'executing' ? 'bg-emerald-400' :
              'bg-gray-600'
            )}
            style={{ left: '0', top: '0', height: '85px' }}
          />
          {/* Horizontal left to Researcher */}
          <div
            className={cn(
              'absolute h-0.5 transition-all duration-300',
              conn(a2aStatus, researcherStatus) === 'completed' ? 'bg-emerald-500' :
              conn(a2aStatus, researcherStatus) === 'executing' ? 'bg-emerald-400' :
              'bg-gray-600'
            )}
            style={{ left: '-173px', top: '85px', width: '173px' }}
          />
        </div>
      </div>
    </div>
  )
}

export default ProcessFlow
