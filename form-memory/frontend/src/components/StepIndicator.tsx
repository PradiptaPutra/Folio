import { cn } from '@/lib/utils'

interface StepIndicatorProps {
  steps: string[]
  currentStep: number
}

export function StepIndicator({ steps, currentStep }: StepIndicatorProps) {
  return (
    <div className="w-full mb-12">
      <div className="flex items-center justify-between relative">
        {/* Connection lines */}
        <div className="absolute top-6 left-0 right-0 h-1 bg-border -z-10">
          <div
            className="h-full bg-primary transition-all duration-300"
            style={{
              width: currentStep > 0 ? `${((currentStep) / (steps.length - 1)) * 100}%` : '0%',
            }}
          />
        </div>

        {/* Steps */}
        {steps.map((step, index) => (
          <div key={index} className="flex flex-col items-center">
            <div
              className={cn(
                'relative w-12 h-12 rounded flex items-center justify-center font-bold text-sm transition-all duration-300',
                index <= currentStep
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted text-muted-foreground'
              )}
            >
              {index < currentStep ? '✓' : index + 1}
            </div>
            <span className="text-xs font-medium mt-3 text-center max-w-24">
              {step}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
