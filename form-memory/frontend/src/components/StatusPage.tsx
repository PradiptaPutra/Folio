import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { getEnforcementStatus, type EnforcementStatus, type ApiError } from '@/lib/api'

export function StatusPage() {
  const [status, setStatus] = useState<EnforcementStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const data = await getEnforcementStatus()
        setStatus(data)
      } catch (err) {
        const apiError = err as ApiError
        setError(apiError.detail || apiError.message)
        console.error('Status fetch error:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchStatus()
  }, [])

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <Card>
          <CardContent className="pt-6">
            <p className="text-center text-slate-600">Loading system status...</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <Card className="border-red-200 bg-red-50">
          <CardHeader>
            <CardTitle className="text-red-900">Connection Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-red-700 text-sm mb-4">{error}</p>
            <p className="text-sm text-slate-600">
              Make sure the backend server is running on http://localhost:8000
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* System Status */}
      <Card>
        <CardHeader>
          <CardTitle>System Status</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-slate-600">Status</p>
              <p className="text-lg font-semibold">
                <span className="inline-block w-3 h-3 bg-green-500 rounded-full mr-2"></span>
                {status?.status === 'available' ? 'Available' : 'Unavailable'}
              </p>
            </div>
            <div>
              <p className="text-sm text-slate-600">API Version</p>
              <p className="text-lg font-semibold">{status?.version}</p>
            </div>
          </div>

          {status?.implementation && (
            <div className="pt-4 border-t">
              <p className="text-sm text-slate-600 mb-2">Implementation</p>
              <div className="bg-slate-50 p-3 rounded text-sm space-y-1">
                <p>
                  <strong>Technology:</strong> {status.implementation.technology}
                </p>
                <p>
                  <strong>Version:</strong> {status.implementation.version}
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Enforcement Phases */}
      <Card>
        <CardHeader>
          <CardTitle>Available Enforcement Phases</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {status?.phases && Object.entries(status.phases).map(([phase, details]: [string, any]) => (
              <div key={phase} className="flex items-start gap-3 p-3 bg-slate-50 rounded">
                <div className="flex-shrink-0 mt-1">
                  {details.implemented ? (
                    <span className="text-green-600 font-bold">✓</span>
                  ) : (
                    <span className="text-gray-400">○</span>
                  )}
                </div>
                <div className="flex-1">
                  <p className="font-medium text-sm">{phase}</p>
                  <p className="text-sm text-slate-600">{details.name || details.description}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* API Information */}
      <Card>
        <CardHeader>
          <CardTitle>API Endpoints</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <p className="font-medium text-sm mb-2">GET /enforcement-status</p>
            <p className="text-sm text-slate-600 mb-2">Returns system status and phase information</p>
            <div className="bg-slate-900 text-slate-100 p-3 rounded text-xs font-mono overflow-x-auto">
              <p className="text-green-400">Status: {status?.status}</p>
              <p className="text-green-400">Version: {status?.version}</p>
            </div>
          </div>

          <div className="border-t pt-4">
            <p className="font-medium text-sm mb-2">POST /enforce-and-download</p>
            <p className="text-sm text-slate-600 mb-2">Upload file and enforce with optional front-matter</p>
            <div className="bg-slate-900 text-slate-100 p-3 rounded text-xs font-mono">
              <p className="text-cyan-400">Content-Type: multipart/form-data</p>
              <p className="text-cyan-400">Parameters:</p>
              <p className="ml-4">- file: DOCX file</p>
              <p className="ml-4">- include_frontmatter: boolean</p>
              <p className="ml-4">- judul, penulis, nim, ... (optional)</p>
            </div>
          </div>

          <div className="border-t pt-4">
            <p className="font-medium text-sm mb-2">POST /enforce-skripsi</p>
            <p className="text-sm text-slate-600 mb-2">Enforce pre-uploaded document</p>
            <div className="bg-slate-900 text-slate-100 p-3 rounded text-xs font-mono">
              <p className="text-cyan-400">Content-Type: application/json</p>
              <p className="text-cyan-400">Parameters:</p>
              <p className="ml-4">- filename: string</p>
              <p className="ml-4">- include_frontmatter: boolean</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
