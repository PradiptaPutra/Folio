import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { FileUpload } from '@/components/FileUpload'
import { StepIndicator } from '@/components/StepIndicator'
import { DetailsForm } from '@/components/DetailsForm'
import { ProcessingView } from '@/components/ProcessingView'
import { SuccessView } from '@/components/SuccessView'
import {
  analyzeTemplate,
  extractContent,
  formatThesis,
  downloadFile,
  type ApiError,
  type TemplateAnalysis,
  type ContentExtraction,
} from '@/lib/api'
import { CheckCircle } from 'lucide-react'

export function UniversalFormatter() {
  // File states
  const [templateFile, setTemplateFile] = useState<File | null>(null)
  const [contentFile, setContentFile] = useState<File | null>(null)

  // User data
  const [userData, setUserData] = useState({
    title: '',
    author: '',
    nim: '',
    advisor: '',
    institution: '',
    date: new Date().toISOString().split('T')[0],
  })

  // Analysis states
  const [templateAnalysis, setTemplateAnalysis] = useState<TemplateAnalysis | null>(null)
  const [contentExtraction, setContentExtraction] = useState<ContentExtraction | null>(null)

  // UI states
  const [currentStep, setCurrentStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [results, setResults] = useState<any>(null)

  const [processingSteps, setProcessingSteps] = useState([
    { label: 'Analyzing template structure', completed: false, processing: false },
    { label: 'Extracting content sections', completed: false, processing: false },
    { label: 'Mapping content to template', completed: false, processing: false },
    { label: 'Applying formatting rules', completed: false, processing: false },
    { label: 'Generating final document', completed: false, processing: false },
  ])

  const handleTemplateFileSelect = async (file: File) => {
    setTemplateFile(file)
    setError(null)
    setTemplateAnalysis(null)

    // Auto-analyze template
    setLoading(true)
    try {
      const analysis = await analyzeTemplate(file)
      setTemplateAnalysis(analysis)
      setSuccess(true)
    } catch (err) {
      const apiError = err as ApiError
      setError(`Template analysis failed: ${apiError.detail || apiError.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleContentFileSelect = async (file: File) => {
    setContentFile(file)
    setError(null)
    setContentExtraction(null)

    // Auto-extract content
    setLoading(true)
    try {
      const extraction = await extractContent(file)
      setContentExtraction(extraction)
      setSuccess(true)
    } catch (err) {
      const apiError = err as ApiError
      setError(`Content extraction failed: ${apiError.detail || apiError.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleDetailsSubmit = (data: any) => {
    setUserData({
      ...data,
      date: data.date || new Date().toISOString().split('T')[0],
    })
    setCurrentStep(2)
  }

  const handleFormatThesisClick = async () => {
    if (!templateFile || !contentFile) {
      setError('Please select both template and content files')
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(false)
    setCurrentStep(2)

    // Simulate processing
    for (let i = 0; i < processingSteps.length; i++) {
      setProcessingSteps((prev) =>
        prev.map((step, idx) => ({
          ...step,
          processing: idx === i,
          completed: idx < i,
        }))
      )
      await new Promise((resolve) => setTimeout(resolve, 800))
    }

    try {
      const { blob, filename } = await formatThesis(templateFile, contentFile, userData)
      downloadFile(blob, filename)

      setSuccess(true)
      setResults({
        message: 'Thesis formatted successfully!',
        filename: filename,
        size: (blob.size / 1024 / 1024).toFixed(2) + ' MB',
        timestamp: new Date().toLocaleString(),
      })
      setCurrentStep(3)
    } catch (err) {
      const apiError = err as ApiError
      setError(apiError.detail || apiError.message || 'Failed to format thesis')
      console.error('Format error:', err)
      setCurrentStep(1)
    } finally {
      setLoading(false)
      setProcessingSteps(
        processingSteps.map((step) => ({
          ...step,
          processing: false,
        }))
      )
    }
  }

  const handleFormatAnother = () => {
    setTemplateFile(null)
    setContentFile(null)
    setUserData({
      title: '',
      author: '',
      nim: '',
      advisor: '',
      institution: '',
      date: new Date().toISOString().split('T')[0],
    })
    setTemplateAnalysis(null)
    setContentExtraction(null)
    setCurrentStep(0)
    setSuccess(false)
    setResults(null)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-6xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="mb-12 space-y-4 animate-fade-in-up">
          <h1 className="text-display">Universal Thesis Formatter</h1>
          <p className="text-body-lg text-muted-foreground max-w-2xl">
            Format your thesis for any university template. Works with any DOCX template worldwide. No configuration needed.
          </p>
        </div>

        {/* Error/Success Messages */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded text-red-700 text-sm animate-fade-in-up">
            ⚠ {error}
          </div>
        )}

        {/* Step Indicator */}
        {currentStep < 3 && (
          <div className="mb-12">
            <StepIndicator
              steps={['Upload Template', 'Upload Content', 'Fill Details']}
              currentStep={currentStep}
            />
          </div>
        )}

        {/* Content */}
        {currentStep === 0 && (
          <div className="space-y-8 animate-fade-in-up">
            {/* Template Upload */}
            <Card className="document-preview">
              <CardHeader>
                <CardTitle>Step 1: Upload Your Template</CardTitle>
                <CardDescription>
                  Select your university's thesis template in DOCX format. Any university worldwide is supported.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <FileUpload
                  onFileSelect={handleTemplateFileSelect}
                  accept=".docx"
                  label="Template DOCX File"
                  description="Upload your university's thesis template"
                />
                {templateFile && (
                  <div className="mt-6 p-4 bg-primary/5 border border-primary rounded flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-primary flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-sm">{templateFile.name}</p>
                      {templateAnalysis && (
                        <p className="text-xs text-muted-foreground mt-1">
                          Template analyzed: {templateAnalysis.analysis.front_matter_sections?.length || 0} sections detected
                        </p>
                      )}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Content Upload */}
            {templateFile && (
              <Card className="document-preview">
                <CardHeader>
                  <CardTitle>Step 2: Upload Your Content</CardTitle>
                  <CardDescription>
                    Select your thesis content in DOCX or TXT format. The system will extract sections automatically.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <FileUpload
                    onFileSelect={handleContentFileSelect}
                    accept=".docx,.txt"
                    label="Content File (DOCX or TXT)"
                    description="Your thesis content or chapters"
                  />
                  {contentFile && (
                    <div className="mt-6 p-4 bg-primary/5 border border-primary rounded flex items-center gap-3">
                      <CheckCircle className="w-5 h-5 text-primary flex-shrink-0" />
                      <div>
                        <p className="font-semibold text-sm">{contentFile.name}</p>
                        {contentExtraction && (
                          <p className="text-xs text-muted-foreground mt-1">
                            {contentExtraction.section_count} sections extracted
                          </p>
                        )}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Next Button */}
            {templateFile && contentFile && (
              <div className="flex justify-center">
                <Button
                  onClick={() => setCurrentStep(1)}
                  disabled={loading}
                  className="btn-hero"
                >
                  Continue to Details
                </Button>
              </div>
            )}
          </div>
        )}

        {/* Details Form */}
        {currentStep === 1 && (
          <Card className="document-preview max-w-2xl mx-auto animate-fade-in-up">
            <CardHeader>
              <CardTitle>Step 3: Fill Thesis Details</CardTitle>
              <CardDescription>
                Enter your information to complete the formatting
              </CardDescription>
            </CardHeader>
            <CardContent>
              <DetailsForm onSubmit={handleDetailsSubmit} isLoading={loading} />
              <div className="flex gap-4 mt-6">
                <button
                  onClick={handleFormatThesisClick}
                  disabled={loading}
                  className="btn-hero flex-1"
                >
                  Format Thesis
                </button>
                <button
                  onClick={() => setCurrentStep(0)}
                  className="btn-outline flex-1"
                >
                  Back
                </button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Processing View */}
        {currentStep === 2 && !success && (
          <div className="animate-fade-in-up">
            <ProcessingView steps={processingSteps} />
          </div>
        )}

        {/* Success View */}
        {currentStep === 3 && success && results && (
          <div className="animate-fade-in-up">
            <SuccessView
              fileName={results.filename}
              onDownload={() => {
                // Re-download from results
                downloadFile(results.blob, results.filename)
              }}
              onFormatAnother={handleFormatAnother}
            />
          </div>
        )}
      </div>
    </div>
  )
}
