import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { StepIndicator } from '@/components/StepIndicator'
import { ProcessingView } from '@/components/ProcessingView'
import { SuccessView } from '@/components/SuccessView'
import { ContentStructureVisualizer } from '@/components/ContentStructureVisualizer'

import { generateFromTemplate, downloadFile, validateTemplate, previewGeneratedDocument, downloadGeneratedDocument, type ApiError } from '@/lib/api'
import { Upload, Eye, FileText } from 'lucide-react'

export function TemplateGenerator() {
  // Step Management
  const [currentStep, setCurrentStep] = useState<0 | 1 | 2 | 3>(0)
  const steps = ['TEMPLATE', 'CONTENT', 'DETAILS', 'GENERATE']

  // File State
  const [templateFile, setTemplateFile] = useState<File | null>(null)
  const [contentFile, setContentFile] = useState<File | null>(null)
  const [rawText, setRawText] = useState<string>('')

  // Metadata State
  const [metadata, setMetadata] = useState({
    judul: '',
    penulis: '',
    nim: '',
    universitas: '',
    dosen_pembimbing: '',
    tahun: new Date().getFullYear().toString(),
    abstrak_teks: '',
    abstrak_en_teks: '',
    kata_kunci: ''
  })

  // Processing State
  const [showPreview, setShowPreview] = useState(false)
  const [processing, setProcessing] = useState(false)
  const [processingSteps, setProcessingSteps] = useState<Array<{ label: string; completed: boolean; processing: boolean }>>([])
  const [templateMetadata, setTemplateMetadata] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [results, setResults] = useState<any>(null)
  
  // AI & Frontmatter Settings
  const [useAI, setUseAI] = useState(true)
  const [includeFrontmatter, setIncludeFrontmatter] = useState(true)

  // Preview State
  const [previewContent, setPreviewContent] = useState<string>('')

  // Content Analysis State
  const [contentAnalysis, setContentAnalysis] = useState<{
    sections: any[]
    wordCount: number
    aiConfidence: number
    missingSections: string[]
  } | null>(null)

  // Content Analysis
  const analyzeContent = () => {
    // Simulate content analysis (in real implementation, this would call backend)
    const sections = [
      {
        title: "BAB I: PENDAHULUAN",
        content: ["This is the introduction section"],
        level: 1,
        type: "chapter",
        confidence: 0.95
      },
      {
        title: "BAB II: TINJAUAN PUSTAKA",
        content: ["This is the literature review section"],
        level: 1,
        type: "chapter",
        confidence: 0.92
      }
    ]

    const wordCount = rawText.split(' ').length
    const missingSections = ["BAB III: METODE PENELITIAN", "BAB IV: HASIL DAN PEMBAHASAN", "BAB V: KESIMPULAN"]

    setContentAnalysis({
      sections,
      wordCount,
      aiConfidence: 0.87,
      missingSections
    })
  }

  // Event Handlers
  const handleInputChange = (field: string, value: string) => {
    setMetadata(prev => ({ ...prev, [field]: value }))
  }

  // Step 1: Template Upload
  const handleTemplateChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    
    if (!file.name.endsWith('.docx')) {
      setError('Please select a valid .docx template file')
      return
    }

    setTemplateFile(file)
    setError(null)
    setProcessing(true)

    // Validate template
    try {
      const metadata = await validateTemplate(file)
      setTemplateMetadata(metadata)
      setCurrentStep(1)
    } catch (err) {
      const apiError = err as ApiError
      setError(`Template validation failed: ${apiError.detail || apiError.message}`)
    } finally {
      setProcessing(false)
    }
  }

  // Step 2: Content Upload
  const handleContentChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (file.name.endsWith('.txt')) {
      setContentFile(file)
      const reader = new FileReader()
      reader.onload = (event) => {
        setRawText(event.target?.result as string)
        setError(null)
      }
      reader.readAsText(file)
    } else {
      setError('Please upload a .txt file')
    }
  }

  const handleContentPaste = (text: string) => {
    setRawText(text)
    // Don't clear the contentFile, keep both options available
    setError(null)
    // Analyze content structure
    analyzeContent()
  }

  const handleNextStep = () => {
    if (currentStep === 0 && !templateFile) {
      setError('Please upload a template file')
      return
    }
    if (currentStep === 1 && !rawText.trim()) {
      setError('Please provide content')
      return
    }
    if (currentStep < 3) {
      setCurrentStep((currentStep + 1) as 0 | 1 | 2 | 3)
    }
  }

  const handlePreviousStep = () => {
    if (currentStep > 0) {
      setCurrentStep((currentStep - 1) as 0 | 1 | 2 | 3)
    }
  }

  // Preview Handler
  const handlePreview = () => {
    setShowPreview(true)
  }

  // Generate Document
  const handleGenerate = async () => {
    if (!templateFile || !rawText.trim()) {
      setError('Missing template or content')
      return
    }

    setProcessing(true)
    setShowPreview(false)
    setProcessingSteps([
      { label: 'Analyzing template structure', completed: false, processing: true },
      { label: 'Extracting content sections', completed: false, processing: false },
      { label: 'Mapping content to template', completed: false, processing: false },
      { label: 'Applying formatting rules', completed: false, processing: false },
      { label: 'Generating final document', completed: false, processing: false },
    ])

    try {
      // Simulate step-by-step progress
      await new Promise(resolve => setTimeout(resolve, 500))
      setProcessingSteps(s => [{ ...s[0], completed: true, processing: false }, { ...s[1], processing: true }, ...s.slice(2)])

      await new Promise(resolve => setTimeout(resolve, 500))
      setProcessingSteps(s => [s[0], { ...s[1], completed: true, processing: false }, { ...s[2], processing: true }, ...s.slice(3)])

      await new Promise(resolve => setTimeout(resolve, 500))
      setProcessingSteps(s => [s[0], s[1], { ...s[2], completed: true, processing: false }, { ...s[3], processing: true }, s[4]])

      await new Promise(resolve => setTimeout(resolve, 500))
      setProcessingSteps(s => [s[0], s[1], s[2], { ...s[3], completed: true, processing: false }, { ...s[4], processing: true }])

      // Generate actual document
      const result = await generateFromTemplate(
        templateFile,
        rawText,
        {
          ...metadata,
          tahun: parseInt(metadata.tahun) || 2024
        },
        includeFrontmatter,  // use state value
        useAI   // use state value
      )

      await new Promise(resolve => setTimeout(resolve, 500))
      setProcessingSteps(s => [...s.slice(0, 4), { ...s[4], completed: true, processing: false }])

      // Store results for later use
      setResults(result)

      // Download automatically
      try {
        const blob = await downloadGeneratedDocument(result.filename)
        downloadFile(blob, result.filename)
      } catch (downloadError) {
        console.error('Auto-download failed:', downloadError)
        // Continue to success screen even if download fails
      }

      // Success
      await new Promise(resolve => setTimeout(resolve, 1000))
      setProcessing(false)
      setSuccess(true)

    } catch (err) {
      const apiError = err as ApiError
      setError(apiError.detail || apiError.message || 'Failed to generate document')
    } finally {
      setProcessing(false)
    }
  }

  // Reset
  const handleReset = () => {
    setCurrentStep(0)
    setTemplateFile(null)
    setContentFile(null)
    setRawText('')
    setMetadata({
      judul: '',
      penulis: '',
      nim: '',
      universitas: '',
      dosen_pembimbing: '',
      tahun: new Date().getFullYear().toString(),
      abstrak_teks: '',
      abstrak_en_teks: '',
      kata_kunci: ''
    })
    setShowPreview(false)
    setProcessing(false)
    setSuccess(false)
    setError(null)
  }

  // Show success view
  if (success) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <SuccessView
          fileName={results?.filename || 'thesis.docx'}
          onDownload={async () => {
            try {
              const blob = await downloadGeneratedDocument(results?.filename || 'thesis.docx')
              downloadFile(blob, results?.filename || 'thesis.docx')
            } catch (error) {
              console.error('Download failed:', error)
              alert('Download failed. Please try again.')
            }
          }}
          onFormatAnother={handleReset}
          onPreview={async () => {
            try {
              const result = await previewGeneratedDocument(results?.filename || 'thesis.docx')
              setPreviewContent(result.html_content)
            } catch (error) {
              console.error('Preview failed:', error)
              alert('Preview not available')
            }
          }}
          previewContent={previewContent}
        />
      </div>
    )
  }

  // Show processing view
  if (processing) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="space-y-8">
          <div className="text-center space-y-2">
            <h2 className="text-3xl font-bold">Generating Your Thesis</h2>
            <p className="text-muted-foreground">Please wait while we format your document with AI analysis...</p>
          </div>
          <ProcessingView steps={processingSteps} />
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">
      {/* Step Indicator */}
      <StepIndicator steps={steps} currentStep={currentStep} />

      {/* Step 1: Template Upload */}
      {currentStep === 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Step 1: Upload Template</CardTitle>
            <CardDescription>
              Select your university's thesis template (DOCX format)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Drag & Drop Area */}
            <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary transition-colors cursor-pointer">
              <label className="cursor-pointer flex flex-col items-center gap-3">
                <Upload className="w-8 h-8 text-muted-foreground" />
                <div>
                  <p className="font-semibold">Click to upload or drag and drop</p>
                  <p className="text-sm text-muted-foreground">DOCX file (up to 50MB)</p>
                </div>
                <input
                  type="file"
                  accept=".docx"
                  onChange={handleTemplateChange}
                  className="hidden"
                />
              </label>
            </div>

            {templateFile && (
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm font-semibold text-green-900">✓ Template selected</p>
                <p className="text-sm text-green-700">{templateFile.name}</p>
              </div>
            )}

            {templateMetadata && (
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg space-y-2">
                <p className="text-sm font-semibold text-blue-900">Template Info</p>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-blue-700/70">Styles Detected</p>
                    <p className="font-semibold text-blue-900">{Object.keys(templateMetadata.styles || {}).length}</p>
                  </div>
                  <div>
                    <p className="text-blue-700/70">Margins Configured</p>
                    <p className="font-semibold text-blue-900">Yes</p>
                  </div>
                </div>
              </div>
            )}

            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg space-y-1">
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-2a1 1 0 00-2 0v8a1 1 0 002 0v-8z" clipRule="evenodd"/>
                  </svg>
                  <p className="text-sm font-semibold text-red-900">Error</p>
                </div>
                <p className="text-sm text-red-700 break-words">{error}</p>
              </div>
            )}

            {processing && (
              <div className="flex items-center justify-center py-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                <p className="ml-3 text-sm text-muted-foreground">Validating template...</p>
              </div>
            )}

            <Button
              onClick={handleNextStep}
              disabled={!templateFile || processing}
              className="w-full"
            >
              {processing ? 'Validating...' : 'Continue to Content'}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Step 2: Content Upload */}
      {currentStep === 1 && (
        <Card>
          <CardHeader>
            <CardTitle>Step 2: Upload Content</CardTitle>
            <CardDescription>
              Provide your thesis content (chapters, sections)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* File Upload */}
            <div>
              <label className="block text-sm font-medium mb-2">Upload Text File</label>
              <div className="border-2 border-dashed border-border rounded-lg p-6 text-center hover:border-primary transition-colors">
                <label className="cursor-pointer flex flex-col items-center gap-2">
                  <FileText className="w-6 h-6 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">Click to upload</p>
                    <p className="text-xs text-muted-foreground">TXT file</p>
                  </div>
                  <input
                    type="file"
                    accept=".txt"
                    onChange={handleContentChange}
                    className="hidden"
                  />
                </label>
              </div>
            </div>

            {contentFile && (
              <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm font-semibold text-green-900">✓ Loaded: {contentFile.name}</p>
              </div>
            )}

            {/* Or Text Area */}
            <div>
              <label className="block text-sm font-medium mb-2">Or Paste Content Directly</label>
              <textarea
                value={rawText}
                onChange={(e) => handleContentPaste(e.target.value)}
                placeholder="Paste your thesis chapters here...

BAB I: INTRODUCTION
...

BAB II: LITERATURE REVIEW
..."
                className="w-full h-48 p-4 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary font-mono text-sm"
              />
              <p className="text-xs text-muted-foreground mt-2">{rawText.length} characters</p>
            </div>

            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            {/* Content Structure Analysis */}
            {contentAnalysis && (
              <div className="mt-6">
                <ContentStructureVisualizer
                  sections={contentAnalysis.sections}
                  totalWordCount={contentAnalysis.wordCount}
                  aiConfidence={contentAnalysis.aiConfidence}
                  missingSections={contentAnalysis.missingSections}
                />
              </div>
            )}

            {/* Navigation */}
            <div className="flex gap-3">
              <Button
                onClick={handlePreviousStep}
                variant="outline"
                className="flex-1"
              >
                Back
              </Button>
              <Button
                onClick={handleNextStep}
                disabled={!rawText.trim()}
                className="flex-1"
              >
                Continue to Details
              </Button>
            </div>
           </CardContent>
        </Card>
      )}

      {/* Step 3: Details Form */}


      {currentStep === 2 && (
        <Card>
          <CardHeader>
            <CardTitle>Step 3: Your Details</CardTitle>
            <CardDescription>
              Personal and thesis information for document
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* AI & Frontmatter Settings */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="block text-sm font-medium">Use AI Analysis</label>
                <select
                  value={String(useAI)}
                  onChange={(e) => setUseAI(e.target.value === 'true')}
                  className="w-full px-4 py-2 border border-border rounded focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="true">Yes (Recommended)</option>
                  <option value="false">No</option>
                </select>
                <p className="text-xs text-muted-foreground">AI detects chapters and sections intelligently</p>
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-medium">Include Front Matter</label>
                <select
                  value={String(includeFrontmatter)}
                  onChange={(e) => setIncludeFrontmatter(e.target.value === 'true')}
                  className="w-full px-4 py-2 border border-border rounded focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="true">Yes (Recommended)</option>
                  <option value="false">No</option>
                </select>
                <p className="text-xs text-muted-foreground">Add title page, approvals, abstracts, etc.</p>
              </div>
            </div>

             <div className="border-t border-border pt-6">
              <h3 className="text-sm font-medium mb-4">Thesis Information</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Full Name */}
              <div className="space-y-2">
                <label className="block text-sm font-medium">Full Name *</label>
                <input
                  type="text"
                  value={metadata.penulis}
                  onChange={(e) => handleInputChange('penulis', e.target.value)}
                  placeholder="John Doe"
                  className="w-full px-4 py-2 border border-border rounded focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              {/* Student ID */}
              <div className="space-y-2">
                <label className="block text-sm font-medium">Student ID / NIM *</label>
                <input
                  type="text"
                  value={metadata.nim}
                  onChange={(e) => handleInputChange('nim', e.target.value)}
                  placeholder="20230001"
                  className="w-full px-4 py-2 border border-border rounded focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              {/* Thesis Title */}
              <div className="md:col-span-2 space-y-2">
                <label className="block text-sm font-medium">Thesis Title *</label>
                <input
                  type="text"
                  value={metadata.judul}
                  onChange={(e) => handleInputChange('judul', e.target.value)}
                  placeholder="Enter your thesis title..."
                  className="w-full px-4 py-2 border border-border rounded focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              {/* Advisor Name */}
              <div className="space-y-2">
                <label className="block text-sm font-medium">Advisor Name *</label>
                <input
                  type="text"
                  value={metadata.dosen_pembimbing}
                  onChange={(e) => handleInputChange('dosen_pembimbing', e.target.value)}
                  placeholder="Dr. Jane Smith"
                  className="w-full px-4 py-2 border border-border rounded focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              {/* University */}
              <div className="space-y-2">
                <label className="block text-sm font-medium">University *</label>
                <input
                  type="text"
                  value={metadata.universitas}
                  onChange={(e) => handleInputChange('universitas', e.target.value)}
                  placeholder="Universitas Indonesia"
                  className="w-full px-4 py-2 border border-border rounded focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              {/* Abstract ID */}
              <div className="md:col-span-2 space-y-2">
                <label className="block text-sm font-medium">Abstract (Indonesian)</label>
                <textarea
                  value={metadata.abstrak_teks}
                  onChange={(e) => handleInputChange('abstrak_teks', e.target.value)}
                  placeholder="Brief abstract in Indonesian..."
                  className="w-full h-20 p-3 border border-border rounded focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                />
              </div>

              {/* Abstract EN */}
              <div className="md:col-span-2 space-y-2">
                <label className="block text-sm font-medium">Abstract (English)</label>
                <textarea
                  value={metadata.abstrak_en_teks}
                  onChange={(e) => handleInputChange('abstrak_en_teks', e.target.value)}
                  placeholder="Brief abstract in English..."
                  className="w-full h-20 p-3 border border-border rounded focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                />
              </div>
            </div>

            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg space-y-1">
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-2a1 1 0 00-2 0v8a1 1 0 002 0v-8z" clipRule="evenodd"/>
                  </svg>
                  <p className="text-sm font-semibold text-red-900">Error</p>
                </div>
                <p className="text-sm text-red-700 break-words">{error}</p>
              </div>
            )}

            {/* Navigation */}
            <div className="flex gap-3 pt-4">
              <Button
                onClick={handlePreviousStep}
                variant="outline"
                className="flex-1"
              >
                Back
              </Button>
              <Button
                onClick={handlePreview}
                variant="outline"
                className="flex-1"
              >
                <Eye className="w-4 h-4 mr-2" />
                Preview
              </Button>
              <Button
                onClick={handleGenerate}
                className="flex-1"
              >
                Start Formatting
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Preview Modal */}
      {showPreview && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="max-w-2xl w-full max-h-96 overflow-y-auto">
            <CardHeader>
              <CardTitle>Preview Formatted Output</CardTitle>
              <button
                onClick={() => setShowPreview(false)}
                className="absolute top-4 right-4 text-muted-foreground hover:text-foreground"
              >
                ✕
              </button>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div>
                  <p className="text-xs font-medium text-muted-foreground">DETECTED STRUCTURE</p>
                  <div className="mt-2 space-y-1 text-sm">
                    <p className="flex items-center gap-2"><span className="text-primary">✓</span>Cover Page</p>
                    <p className="flex items-center gap-2"><span className="text-primary">✓</span>Approval Page</p>
                    <p className="flex items-center gap-2"><span className="text-primary">✓</span>Abstract (Indonesian & English)</p>
                    <p className="flex items-center gap-2"><span className="text-primary">✓</span>Table of Contents</p>
                    <p className="flex items-center gap-2"><span className="text-primary">✓</span>List of Figures</p>
                    <p className="flex items-center gap-2"><span className="text-primary">✓</span>List of Tables</p>
                    <p className="flex items-center gap-2"><span className="text-primary">✓</span>Chapters</p>
                    <p className="flex items-center gap-2"><span className="text-primary">✓</span>References</p>
                  </div>
                </div>

                <div className="pt-2 border-t">
                  <p className="text-xs font-medium text-muted-foreground">APPLIED FORMATTING</p>
                  <div className="mt-2 grid grid-cols-2 gap-2 text-sm">
                    <div className="p-2 bg-muted rounded">
                      <p className="text-xs text-muted-foreground">Font</p>
                      <p className="font-medium">Times New Roman, 12pt</p>
                    </div>
                    <div className="p-2 bg-muted rounded">
                      <p className="text-xs text-muted-foreground">Margins</p>
                      <p className="font-medium">4cm left, 3cm others</p>
                    </div>
                    <div className="p-2 bg-muted rounded">
                      <p className="text-xs text-muted-foreground">Spacing</p>
                      <p className="font-medium">1.5 line spacing</p>
                    </div>
                    <div className="p-2 bg-muted rounded">
                      <p className="text-xs text-muted-foreground">Citation Style</p>
                      <p className="font-medium">APA 6th Edition</p>
                    </div>
                  </div>
                </div>

                <div className="pt-2 border-t bg-primary/5 p-3 rounded">
                  <p className="text-xs font-medium text-primary">AI SEMANTIC ANALYSIS</p>
                  <p className="text-sm text-primary/80 mt-1">Document structure will be analyzed with AI to intelligently detect chapters, sections, and content organization.</p>
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <Button
                  onClick={() => setShowPreview(false)}
                  variant="outline"
                  className="flex-1"
                >
                  Back
                </Button>
                <Button
                  onClick={() => {
                    setShowPreview(false)
                    handleGenerate()
                  }}
                  className="flex-1"
                >
                  Start Formatting
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
