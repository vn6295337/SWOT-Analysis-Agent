import { useState, useEffect, useRef, useCallback } from "react"
import { cn } from "@/lib/utils"
import { Input } from "@/components/ui/input"
import { Search, X, Check, Loader2 } from "lucide-react"
import { searchStocks, StockResult } from "@/lib/api"

interface StockSearchProps {
  onSelect: (stock: StockResult) => void
  disabled?: boolean
  selectedStock?: StockResult | null
  onClear?: () => void
}

export function StockSearch({
  onSelect,
  disabled = false,
  selectedStock,
  onClear,
}: StockSearchProps) {
  const [query, setQuery] = useState("")
  const [results, setResults] = useState<StockResult[]>([])
  const [isOpen, setIsOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [highlightedIndex, setHighlightedIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const listRef = useRef<HTMLDivElement>(null)
  const debounceRef = useRef<NodeJS.Timeout>()

  // Debounced search
  const performSearch = useCallback(async (searchQuery: string) => {
    if (searchQuery.length < 1) {
      setResults([])
      setIsOpen(false)
      return
    }

    setIsLoading(true)
    try {
      const response = await searchStocks(searchQuery)
      setResults(response.results)
      setIsOpen(response.results.length > 0)
      setHighlightedIndex(0)
    } catch (error) {
      console.error("Stock search error:", error)
      setResults([])
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current)
    }

    debounceRef.current = setTimeout(() => {
      performSearch(query)
    }, 150) // 150ms debounce

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current)
      }
    }
  }, [query, performSearch])

  // Keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) return

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault()
        setHighlightedIndex((prev) =>
          prev < results.length - 1 ? prev + 1 : prev
        )
        break
      case "ArrowUp":
        e.preventDefault()
        setHighlightedIndex((prev) => (prev > 0 ? prev - 1 : 0))
        break
      case "Enter":
        e.preventDefault()
        if (results[highlightedIndex]) {
          handleSelect(results[highlightedIndex])
        }
        break
      case "Escape":
        e.preventDefault()
        setIsOpen(false)
        inputRef.current?.blur()
        break
    }
  }

  const handleSelect = (stock: StockResult) => {
    onSelect(stock)
    setQuery("")
    setIsOpen(false)
    setResults([])
  }

  const handleClear = () => {
    setQuery("")
    setResults([])
    setIsOpen(false)
    onClear?.()
    inputRef.current?.focus()
  }

  // Close on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        listRef.current &&
        !listRef.current.contains(e.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(e.target as Node)
      ) {
        setIsOpen(false)
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  // Show selected stock
  if (selectedStock) {
    return (
      <div className="relative">
        <div className="flex items-center gap-2 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg">
          <Check className="w-4 h-4 text-emerald-500" />
          <div className="flex-1">
            <span className="font-medium text-white">
              {selectedStock.name}
            </span>
            <span className="text-gray-400 ml-2">
              ({selectedStock.symbol})
            </span>
          </div>
          <span className="text-xs text-gray-500 px-2 py-0.5 bg-gray-700 rounded">
            {selectedStock.exchange}
          </span>
          {!disabled && (
            <button
              onClick={handleClear}
              className="p-1 hover:bg-gray-700 rounded transition-colors"
            >
              <X className="w-4 h-4 text-gray-400" />
            </button>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="relative">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <Input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => query.length > 0 && results.length > 0 && setIsOpen(true)}
          placeholder="Search U.S. listed companies..."
          disabled={disabled}
          className="pl-10 pr-10 bg-gray-800 border-gray-700 focus:border-primary"
        />
        {isLoading && (
          <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 animate-spin" />
        )}
        {!isLoading && query && (
          <button
            onClick={() => {
              setQuery("")
              setResults([])
              setIsOpen(false)
            }}
            className="absolute right-3 top-1/2 -translate-y-1/2 p-0.5 hover:bg-gray-700 rounded"
          >
            <X className="w-4 h-4 text-gray-400" />
          </button>
        )}
      </div>

      <div className="mt-1 text-xs text-gray-500">
        NYSE | NASDAQ | AMEX
      </div>

      {/* Dropdown */}
      {isOpen && results.length > 0 && (
        <div
          ref={listRef}
          className="absolute z-50 w-full mt-1 bg-gray-800 border border-gray-700 rounded-lg shadow-xl overflow-hidden"
        >
          <div className="max-h-64 overflow-y-auto">
            {results.map((stock, index) => (
              <button
                key={stock.symbol}
                onClick={() => handleSelect(stock)}
                onMouseEnter={() => setHighlightedIndex(index)}
                className={cn(
                  "w-full flex items-center gap-3 px-3 py-2 text-left transition-colors",
                  index === highlightedIndex
                    ? "bg-gray-700"
                    : "hover:bg-gray-750"
                )}
              >
                <span className="font-mono font-medium text-white min-w-[60px]">
                  {stock.symbol}
                </span>
                <span className="flex-1 text-sm text-gray-300 truncate">
                  {stock.name}
                </span>
                <span className="text-xs text-gray-500 px-2 py-0.5 bg-gray-700 rounded">
                  {stock.exchange}
                </span>
              </button>
            ))}
          </div>
          <div className="px-3 py-2 border-t border-gray-700 text-xs text-gray-500">
            Up/Down to navigate | Enter to select | Esc to close
          </div>
        </div>
      )}
    </div>
  )
}

export default StockSearch
