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
    <div className="w-full max-w-2xl mx-auto py-16">
      {/* Header */}
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Formatting in progress</h2>
        <p className="text-gray-500">Your thesis is being processed</p>
      </div>

      {/* Steps Container */}
      <div className="relative">
        {/* Left border indicator */}
        <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-red-500 via-red-500 to-gray-300" />

        <div className="ml-6 space-y-4">
          {steps.map((step, index) => (
            <div key={index} className="flex items-start gap-4 pb-2">
              {/* Status Icon */}
              <div className="flex-shrink-0 mt-1">
                {step.completed ? (
                  <div className="w-8 h-8 rounded bg-red-500 text-white flex items-center justify-center flex-shrink-0">
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" />
                    </svg>
                  </div>
                ) : step.processing ? (
                  <div className="w-8 h-8 rounded bg-red-500 text-white flex items-center justify-center flex-shrink-0 animate-spin">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                ) : (
                  <div className="w-8 h-8 rounded bg-gray-200 text-gray-500 flex items-center justify-center flex-shrink-0 text-sm font-medium">
                    {index + 1}
                  </div>
                )}
              </div>

              {/* Step Label */}
              <div className="flex-grow pt-1">
                <p
                  className={`font-semibold ${
                    step.completed
                      ? 'text-gray-900'
                      : step.processing
                        ? 'text-red-500'
                        : 'text-gray-500'
                  }`}
                >
                  {step.label}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
