import { useState } from 'react'
import { TemplateGenerator } from '@/components/TemplateGenerator'
import { DocumentUploader } from '@/components/DocumentUploader'
import { StatusPage } from '@/components/StatusPage'
import { Button } from '@/components/ui/button'

type Page = 'home' | 'generate' | 'enforce' | 'status'

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('home')

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-blue-600">Form Memory</h1>
            <span className="text-sm text-slate-600">Skripsi Formatter</span>
          </div>

          <div className="flex gap-2">
            <Button
              onClick={() => setCurrentPage('home')}
              variant={currentPage === 'home' ? 'default' : 'outline'}
              className="cursor-pointer"
            >
              Home
            </Button>
            <Button
              onClick={() => setCurrentPage('generate')}
              variant={currentPage === 'generate' ? 'default' : 'outline'}
              className="cursor-pointer"
            >
              From Template
            </Button>
            <Button
              onClick={() => setCurrentPage('enforce')}
              variant={currentPage === 'enforce' ? 'default' : 'outline'}
              className="cursor-pointer"
            >
              Fix Existing Doc
            </Button>
            <Button
              onClick={() => setCurrentPage('status')}
              variant={currentPage === 'status' ? 'default' : 'outline'}
              className="cursor-pointer"
            >
              Status
            </Button>
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="py-8">
        {currentPage === 'home' && (
          <div className="max-w-4xl mx-auto px-6">
            <div className="bg-white rounded-lg shadow-sm p-8 mb-8">
              <h2 className="text-3xl font-bold text-slate-900 mb-4">
                Welcome to Form Memory
              </h2>
              <p className="text-lg text-slate-600 mb-6">
                Automatically format your Indonesian thesis (skripsi) according to strict academic standards.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                {/* Feature 1 */}
                <div
                  onClick={() => setCurrentPage('generate')}
                  className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6 cursor-pointer hover:shadow-md transition-shadow"
                >
                  <div className="text-3xl mb-3">📝</div>
                  <h3 className="font-semibold text-slate-900 mb-2">
                    Generate New Document
                  </h3>
                  <p className="text-sm text-slate-700">
                    Create a new thesis document from raw text and a template. Best for starting fresh.
                  </p>
                </div>

                {/* Feature 2 */}
                <div
                  onClick={() => setCurrentPage('enforce')}
                  className="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-lg p-6 cursor-pointer hover:shadow-md transition-shadow"
                >
                  <div className="text-3xl mb-3">🔧</div>
                  <h3 className="font-semibold text-slate-900 mb-2">
                    Fix Existing Document
                  </h3>
                  <p className="text-sm text-slate-700">
                    Upload an existing DOCX file to enforce formatting rules and generate front matter.
                  </p>
                </div>
              </div>

              <div className="bg-slate-50 rounded-lg p-6 border border-slate-200 mb-8">
                <h3 className="font-semibold text-slate-900 mb-3">How It Works</h3>
                <ul className="space-y-2 text-slate-700">
                  <li className="flex gap-2">
                    <span className="text-green-600 font-bold">1</span>
                    <span><strong>Choose Mode:</strong> Generate from scratch or fix an existing file.</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-green-600 font-bold">2</span>
                    <span><strong>Input Metadata:</strong> Enter thesis details (Title, Author, Abstract) for auto-generated pages.</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-green-600 font-bold">3</span>
                    <span><strong>Process:</strong> Our engine applies "Dosen Mode" formatting (strict margins, spacing, numbering).</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-green-600 font-bold">4</span>
                    <span><strong>Download:</strong> Get your perfectly formatted .docx file.</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {currentPage === 'generate' && <TemplateGenerator />}

        {currentPage === 'enforce' && <DocumentUploader />}

        {currentPage === 'status' && <StatusPage />}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 mt-12">
        <div className="max-w-6xl mx-auto px-6 py-6 text-center text-sm text-slate-600">
          <p>Form Memory v1.0.0 | Indonesian Academic Thesis Formatter</p>
        </div>
      </footer>
    </div>
  )
}

export default App
