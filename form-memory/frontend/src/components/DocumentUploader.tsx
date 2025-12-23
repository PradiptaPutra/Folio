import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { 
  type FrontmatterData,
  type ApiError 
} from '@/lib/api'

export function DocumentUploader() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [includeFrontmatter, setIncludeFrontmatter] = useState(false)
  const [frontmatterData, setFrontmatterData] = useState<FrontmatterData>({
    judul: '',
    penulis: '',
    nim: '',
    universitas: '',
    tahun: new Date().getFullYear().toString(),
    abstrak_teks: '',
    abstrak_en_teks: '',
    kata_kunci: '',
  })

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      if (!selectedFile.name.endsWith('.docx')) {
        setError('Please select a valid .docx file')
        return
      }
      setFile(selectedFile)
      setError(null)
      setSuccess(false)
      setResults(null)
    }
  }

  const handleFrontmatterChange = (field: keyof FrontmatterData, value: string) => {
    setFrontmatterData(prev => ({
      ...prev,
      [field]: value,
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!file) {
      setError('Please select a file')
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(false)

    try {
      // Direct DOCX upload workflow is deprecated
      // Use TemplateGenerator component instead (template + content workflow)
      setError('Direct DOCX enforcement is deprecated. Please use the Template Generator workflow instead: 1) Select a template DOCX, 2) Provide content, 3) Generate formatted document.')
    } catch (err) {
      const apiError = err as ApiError
      setError(apiError.detail || apiError.message || 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Skripsi Document Enforcer</CardTitle>
          <CardDescription>
            Upload a DOCX file to apply Indonesian academic formatting standards
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* File Input */}
            <div className="space-y-2">
              <label className="block text-sm font-medium">
                Upload DOCX File
              </label>
              <input
                type="file"
                accept=".docx"
                onChange={handleFileChange}
                disabled={loading}
                className="block w-full text-sm text-slate-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-md file:border-0
                  file:text-sm file:font-semibold
                  file:bg-blue-50 file:text-blue-700
                  hover:file:bg-blue-100
                  disabled:opacity-50"
              />
              {file && (
                <p className="text-sm text-green-600">
                  ✓ Selected: {file.name}
                </p>
              )}
            </div>

            {/* Front-Matter Toggle */}
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="include-frontmatter"
                checked={includeFrontmatter}
                onChange={(e) => setIncludeFrontmatter(e.target.checked)}
                disabled={loading}
                className="rounded border-gray-300"
              />
              <label htmlFor="include-frontmatter" className="text-sm font-medium cursor-pointer">
                Include Front Matter (Title Page, Abstract, etc.)
              </label>
            </div>

            {/* Front-Matter Fields */}
            {includeFrontmatter && (
              <div className="space-y-4 bg-slate-50 p-4 rounded-lg border border-slate-200">
                <h3 className="font-semibold text-sm text-slate-700">Front Matter Information</h3>
                
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Title (Judul) *
                  </label>
                  <input
                    type="text"
                    value={frontmatterData.judul}
                    onChange={(e) => handleFrontmatterChange('judul', e.target.value)}
                    disabled={loading}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                    placeholder="Thesis title in Indonesian"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">
                    Author (Penulis) *
                  </label>
                  <input
                    type="text"
                    value={frontmatterData.penulis}
                    onChange={(e) => handleFrontmatterChange('penulis', e.target.value)}
                    disabled={loading}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                    placeholder="Full name"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">
                      Student ID (NIM) *
                    </label>
                    <input
                      type="text"
                      value={frontmatterData.nim}
                      onChange={(e) => handleFrontmatterChange('nim', e.target.value)}
                      disabled={loading}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                      placeholder="20210001"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">
                      Year (Tahun) *
                    </label>
                    <input
                      type="text"
                      value={frontmatterData.tahun}
                      onChange={(e) => handleFrontmatterChange('tahun', e.target.value)}
                      disabled={loading}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                      placeholder="2024"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">
                    University (Universitas) *
                  </label>
                  <input
                    type="text"
                    value={frontmatterData.universitas}
                    onChange={(e) => handleFrontmatterChange('universitas', e.target.value)}
                    disabled={loading}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                    placeholder="University name"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">
                    Abstract (Indonesian)
                  </label>
                  <textarea
                    value={frontmatterData.abstrak_teks}
                    onChange={(e) => handleFrontmatterChange('abstrak_teks', e.target.value)}
                    disabled={loading}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                    placeholder="Write your abstract in Indonesian..."
                    rows={3}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">
                    Abstract (English)
                  </label>
                  <textarea
                    value={frontmatterData.abstrak_en_teks}
                    onChange={(e) => handleFrontmatterChange('abstrak_en_teks', e.target.value)}
                    disabled={loading}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                    placeholder="Write your abstract in English..."
                    rows={3}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">
                    Keywords (Kata Kunci)
                  </label>
                  <input
                    type="text"
                    value={frontmatterData.kata_kunci}
                    onChange={(e) => handleFrontmatterChange('kata_kunci', e.target.value)}
                    disabled={loading}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                    placeholder="keyword1, keyword2, keyword3"
                  />
                </div>
              </div>
            )}

            {/* Submit Button */}
            <Button
              type="submit"
              disabled={!file || loading}
              className="w-full"
            >
              {loading ? (
                <>
                  <span className="inline-block mr-2">Processing...</span>
                  <span className="inline-block animate-spin">⚙</span>
                </>
              ) : (
                'Enforce & Download Document'
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Success Message */}
      {success && results && (
        <Card className="border-green-200 bg-green-50">
          <CardHeader>
            <CardTitle className="text-green-900">Success!</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p className="text-green-700">
              ✓ Your document has been formatted and is ready for download.
            </p>
            <p>
              <strong>File:</strong> {results.filename}
            </p>
            <p>
              <strong>Size:</strong> {(results.size / 1024).toFixed(2)} KB
            </p>
            <p>
              <strong>Processed:</strong> {results.timestamp}
            </p>
          </CardContent>
        </Card>
      )}

      {/* Error Message */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardHeader>
            <CardTitle className="text-red-900">Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-red-700 text-sm">{error}</p>
            <button
              onClick={() => setError(null)}
              className="mt-2 text-red-600 text-sm hover:underline"
            >
              Dismiss
            </button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
