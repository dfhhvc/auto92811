import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

interface ScoreBadgeProps {
  score: number
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
}

export default function ScoreBadge({ score, size = 'md', showLabel = false }: ScoreBadgeProps) {
  const color =
    score >= 8.5
      ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
      : score >= 7.0
      ? 'bg-primary-500/20 text-primary-400 border-primary-500/40'
      : score >= 5.0
      ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/40'
      : 'bg-red-500/20 text-red-400 border-red-500/40'

  const sizeClass =
    size === 'sm'
      ? 'text-xs px-1.5 py-0.5'
      : size === 'lg'
      ? 'text-lg px-3 py-1'
      : 'text-sm px-2 py-0.5'

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 font-semibold rounded-lg border',
        color,
        sizeClass
      )}
    >
      {score.toFixed(1)}
      {showLabel && <span className="font-normal opacity-70">/10</span>}
    </span>
  )
}