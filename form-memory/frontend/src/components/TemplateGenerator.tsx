import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { generateFromText, downloadFile, type ApiError } from '@/lib/api'

export function TemplateGenerator() {
  const [templateFile, setTemplateFile] = useState<File | null>(null)
  const [contentFile, setContentFile] = useState<File | null>(null)
  const [rawText, setRawText] = useState<string>('')
  const [outputFormat, setOutputFormat] = useState<'docx' | 'doc'>('docx')

  // Metadata State
  const [metadata, setMetadata] = useState({
    judul: '',
    penulis: '',
    nim: '',
    universitas: '',
    tahun: new Date().getFullYear().toString(),
    abstrak_teks: '',
    abstrak_en_teks: '',
    kata_kunci: ''
  })
  const [includeFrontmatter, setIncludeFrontmatter] = useState(true)

  const [generatingLoading, setGeneratingLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [results, setResults] = useState<any>(null)

  const handleInputChange = (field: string, value: string) => {
    setMetadata(prev => ({ ...prev, [field]: value }))
  }

  const handleTemplateFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      if (!selectedFile.name.endsWith('.docx')) {
        setError('Please select a valid .docx template file')
        return
      }
      setTemplateFile(selectedFile)
      setError(null)
      setSuccess(false)
    }
  }

  const handleContentFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      if (!selectedFile.name.endsWith('.txt')) {
        setError('Please select a valid .txt file for content')
        return
      }
      // Store the file for later use in API call
      setContentFile(selectedFile)

      // Also read and display the content
      const reader = new FileReader()
      reader.onload = (event) => {
        const content = event.target?.result as string
        setRawText(content)
        setError(null)
        setSuccess(false)
      }
      reader.onerror = () => {
        setError('Failed to read the text file')
      }
      reader.readAsText(selectedFile)
    }
  }

  const handleGenerateDocument = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!templateFile) {
      setError('Please select a template file')
      return
    }

    if (!rawText.trim()) {
      setError('Please enter text content or upload a text file')
      return
    }

    setGeneratingLoading(true)
    setError(null)
    setSuccess(false)

    try {
      const { blob, filename } = await generateFromText(
        rawText,
        templateFile, // Send template file directly
        undefined,    // No reference name needed
        outputFormat,
        contentFile || undefined,   // Pass the content file if available
        includeFrontmatter ? {
          ...metadata,
          tahun: parseInt(metadata.tahun) || 2024
        } : undefined,
        includeFrontmatter
      )

      // Download the file
      downloadFile(blob, filename)

      setSuccess(true)
      setResults({
        filename,
        size: blob.size,
        timestamp: new Date().toLocaleString(),
        message: 'Document generated and downloaded successfully',
      })

      // Clear text but keep template
      setRawText('')
      setContentFile(null)
    } catch (err) {
      const apiError = err as ApiError
      setError(apiError.detail || apiError.message || 'Failed to generate document')
      console.error('Generation error:', err)
    } finally {
      setGeneratingLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Generate Document Form */}
      <Card>
        <CardHeader>
          <CardTitle>Generate Formatted Document</CardTitle>
          <CardDescription>
            Upload a template DOCX and raw text content to generate a formatted document
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleGenerateDocument} className="space-y-6">

            {/* Template File */}
            <div className="space-y-2">
              <label className="block text-sm font-medium">Template DOCX File</label>
              <input
                type="file"
                accept=".docx"
                onChange={handleTemplateFileChange}
                disabled={generatingLoading}
                className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 disabled:opacity-50"
              />
              {templateFile && (
                <p className="text-sm text-green-600">✓ Selected: {templateFile.name}</p>
              )}
            </div>

            {/* Metadata Section (Collapsible or always visible) */}
            <div className="space-y-4 border p-4 rounded-md bg-slate-50">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-slate-700">Document Metadata (Front Matter)</h3>
                <label className="flex items-center gap-2 text-sm cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeFrontmatter}
                    onChange={(e) => setIncludeFrontmatter(e.target.checked)}
                    className="rounded border-gray-300"
                  />
                  Enable Auto-Generated Pages
                </label>
              </div>

              {includeFrontmatter && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-xs font-medium">Judul Skripsi</label>
                    <input
                      type="text"
                      value={metadata.judul}
                      onChange={(e) => handleInputChange('judul', e.target.value)}
                      className="w-full p-2 border rounded text-sm"
                      placeholder="JUDUL SKRIPSI..."
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs font-medium">Penulis / Nama</label>
                    <input
                      type="text"
                      value={metadata.penulis}
                      onChange={(e) => handleInputChange('penulis', e.target.value)}
                      className="w-full p-2 border rounded text-sm"
                      placeholder="Nama Mahasiswa"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs font-medium">NIM</label>
                    <input
                      type="text"
                      value={metadata.nim}
                      onChange={(e) => handleInputChange('nim', e.target.value)}
                      className="w-full p-2 border rounded text-sm"
                      placeholder="12345678"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs font-medium">Universitas</label>
                    <input
                      type="text"
                      value={metadata.universitas}
                      onChange={(e) => handleInputChange('universitas', e.target.value)}
                      className="w-full p-2 border rounded text-sm"
                      placeholder="Nama Universitas"
                    />
                  </div>
                  <div className="space-y-1 col-span-2">
                    <label className="text-xs font-medium">Abstrak (Indonesia)</label>
                    <textarea
                      value={metadata.abstrak_teks}
                      onChange={(e) => handleInputChange('abstrak_teks', e.target.value)}
                      className="w-full p-2 border rounded text-sm h-20"
                      placeholder="Isi abstrak..."
                    />
                  </div>
                  <div className="space-y-1 col-span-2">
                    <label className="text-xs font-medium">Abstract (English)</label>
                    <textarea
                      value={metadata.abstrak_en_teks}
                      onChange={(e) => handleInputChange('abstrak_en_teks', e.target.value)}
                      className="w-full p-2 border rounded text-sm h-20"
                      placeholder="English abstract content..."
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Text Area or File Upload */}
            <div className="space-y-2">
              <label className="block text-sm font-medium">Raw Text Content (Body)</label>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <input
                    type="file"
                    accept=".txt"
                    onChange={handleContentFileChange}
                    disabled={generatingLoading}
                    className="flex-1 block text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100 disabled:opacity-50"
                  />
                  <span className="text-xs text-slate-500">or</span>
                </div>
                <textarea
                  value={rawText}
                  onChange={(e) => {
                    setRawText(e.target.value)
                    setContentFile(null)
                  }}
                  disabled={generatingLoading}
                  placeholder="Paste or type your content here... (BAB I, BAB II...)"
                  className="w-full h-48 p-3 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:bg-slate-50 font-mono text-sm"
                />
                {contentFile && (
                  <p className="text-sm text-green-600">✓ Loaded from: {contentFile.name}</p>
                )}
                <p className="text-xs text-slate-500">{rawText.length} characters</p>
              </div>
            </div>

            {/* Output Format */}
            <div className="space-y-2">
              <label className="block text-sm font-medium">Output Format</label>
              <select
                value={outputFormat}
                onChange={(e) => setOutputFormat(e.target.value as 'docx' | 'doc')}
                disabled={generatingLoading}
                className="w-full p-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:bg-slate-50"
              >
                <option value="docx">DOCX (Modern)</option>
                <option value="doc">DOC (Legacy)</option>
              </select>
            </div>

            <Button
              type="submit"
              disabled={generatingLoading || !templateFile || (contentFile === null && !rawText.trim())}
              className="w-full"
            >
              {generatingLoading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Generating Document...
                </>
              ) : (
                'Generate & Download Document'
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Success Message */}
      {success && results && (
        <Card className="border-green-200 bg-green-50">
          <CardContent className="pt-6">
            <div className="space-y-2">
              <h3 className="font-semibold text-green-900">✓ Success!</h3>
              <p className="text-sm text-green-700">{results.message}</p>
              {results.filename && (
                <p className="text-sm text-green-700">
                  <strong>File:</strong> {results.filename}
                </p>
              )}
              {results.size && (
                <p className="text-sm text-green-700">
                  <strong>Size:</strong> {(results.size / 1024).toFixed(2)} KB
                </p>
              )}
              {results.timestamp && (
                <p className="text-sm text-green-700">
                  <strong>Time:</strong> {results.timestamp}
                </p>
              )}
              <p className="text-xs text-green-600 mt-3">
                The file has been automatically downloaded to your downloads folder.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error Message */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-4">
              <div className="flex-1">
                <h3 className="font-semibold text-red-900">✗ Error</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
              <button
                onClick={() => setError(null)}
                className="text-red-600 hover:text-red-800 font-medium text-sm mt-1"
              >
                Dismiss
              </button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Usage Guide */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">How to Use</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 text-sm">
          <div>
            <h4 className="font-semibold mb-2">1. Select Template</h4>
            <p className="text-slate-600">
              Choose a DOCX file that has the formatting, styles, and layout you want to apply to your document.
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-2">2. Enter or Upload Content</h4>
            <p className="text-slate-600">
              Either upload a .txt file with your content, or paste/type your raw text directly in the text area. The system will parse and format it according to the template's styles.
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-2">3. Choose Format</h4>
            <p className="text-slate-600">
              Select output format: DOCX (modern) or DOC (legacy).
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-2">4. Generate & Download</h4>
            <p className="text-slate-600">
              Click the button to generate your formatted document. The file will be automatically downloaded.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
