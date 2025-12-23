interface ProcessingStep {
  label: string
  completed: boolean
  processing: boolean
}

interface ProcessingViewProps {
  steps: ProcessingStep[]
}

export function ProcessingView({ steps }: ProcessingViewProps) {
  return (
    <div className="w-full max-w-2xl mx-auto py-12">
      <div className="space-y-4">
        {steps.map((step, index) => (
          <div
            key={index}
            className="flex items-start gap-4 p-4 border-l-4 transition-all duration-300"
            style={{
              borderLeftColor: step.completed
                ? 'hsl(var(--primary))'
                : step.processing
                  ? 'hsl(var(--primary))'
                  : 'hsl(var(--border))',
              backgroundColor: step.processing ? 'hsl(var(--primary) / 0.05)' : 'transparent',
            }}
          >
            {/* Status Icon */}
            <div className="flex-shrink-0 mt-1">
              {step.completed ? (
                <div className="w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              ) : step.processing ? (
                <div className="w-6 h-6 rounded-full border-2 border-primary border-t-transparent animate-spin" />
              ) : (
                <div className="w-6 h-6 rounded-full border-2 border-border" />
              )}
            </div>

            {/* Content */}
            <div className="flex-grow">
              <p className="font-semibold">{step.label}</p>
              {step.processing && (
                <div className="mt-2 flex gap-1">
                  <span className="w-1 h-1 bg-primary rounded-full animate-pulse-dot" />
                  <span className="w-1 h-1 bg-primary rounded-full animate-pulse-dot stagger-1" />
                  <span className="w-1 h-1 bg-primary rounded-full animate-pulse-dot stagger-2" />
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
