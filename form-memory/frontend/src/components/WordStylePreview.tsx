import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut, Edit, X, FileText } from 'lucide-react'

interface WordStylePreviewProps {
  content: string
  title?: string
  onClose: () => void
  onEdit?: () => void
  showEditButton?: boolean
}

export function WordStylePreview({
  content,
  title = 'Document Preview',
  onClose,
  onEdit,
  showEditButton = true
}: WordStylePreviewProps) {
  const [currentPage, setCurrentPage] = useState(1)
  const [zoom, setZoom] = useState(100)
  const [pages, setPages] = useState<string[]>([])
  const [layoutMode, setLayoutMode] = useState<'web' | 'print'>('print')
  const [showProperties, setShowProperties] = useState(false)
  const contentRef = useRef<HTMLDivElement>(null)

  // Calculate document statistics
  const wordCount = content ? content.replace(/<[^>]*>/g, '').split(/\s+/).length : 0
  const charCount = content ? content.replace(/<[^>]*>/g, '').length : 0

  // Split content into pages based on estimated content height
  useEffect(() => {
    if (!content) return

    const tempDiv = document.createElement('div')
    tempDiv.innerHTML = content
    tempDiv.style.fontFamily = "'Times New Roman', serif"
    tempDiv.style.fontSize = '12pt'
    tempDiv.style.lineHeight = '1.6'
    tempDiv.style.width = '515px' // Content width (595px - margins)
    tempDiv.style.padding = '40px'
    tempDiv.style.position = 'absolute'
    tempDiv.style.visibility = 'hidden'
    tempDiv.style.maxHeight = '702px' // Available height per page (842px - margins)
    document.body.appendChild(tempDiv)

    const pageContents: string[] = []
    let currentPageContent = ''
    const pageHeight = 702 // pixels available for content per page
    let currentHeight = 0

    // Estimate content height and split into pages
    const elements = Array.from(tempDiv.children)
    let i = 0

    while (i < elements.length) {
      const element = elements[i]
      const elementHeight = estimateElementHeight(element)

      // If adding this element would exceed page height, start new page
      if (currentHeight + elementHeight > pageHeight && currentPageContent) {
        pageContents.push(currentPageContent)
        currentPageContent = ''
        currentHeight = 0
      }

      // Force page break for major headings (H1) or if element is too tall
      if (element.tagName === 'H1' && currentPageContent) {
        pageContents.push(currentPageContent)
        currentPageContent = element.outerHTML
        currentHeight = elementHeight
        i++
        continue
      }

      currentPageContent += element.outerHTML
      currentHeight += elementHeight
      i++
    }

    if (currentPageContent) {
      pageContents.push(currentPageContent)
    }

    // Ensure at least one page
    if (pageContents.length === 0) {
      pageContents.push(content)
    }

    document.body.removeChild(tempDiv)
    setPages(pageContents)
    setCurrentPage(1)
  }, [content])

  // Estimate element height (rough calculation)
  const estimateElementHeight = (element: Element): number => {
    const tagName = element.tagName.toLowerCase()
    const heightEstimates = {
      h1: 60,
      h2: 45,
      h3: 35,
      h4: 30,
      h5: 25,
      h6: 20,
      p: 20,
      ul: 25,
      ol: 25,
      li: 20,
      blockquote: 40,
      table: 100,
      tr: 25,
      td: 25,
      th: 25,
      div: 20
    }

    const baseHeight = heightEstimates[tagName as keyof typeof heightEstimates] || 20
    const textContent = element.textContent || ''
    const lines = Math.ceil(textContent.length / 80) // Rough line estimation
    return Math.max(baseHeight, lines * 20)
  }

  const totalPages = pages.length
  const currentPageContent = pages[currentPage - 1] || ''

  const goToPage = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page)
    }
  }

  const zoomIn = () => setZoom(prev => Math.min(prev + 25, 200))
  const zoomOut = () => setZoom(prev => Math.max(prev - 25, 50))
  const fitToPage = () => setZoom(100)
  const fitToWidth = () => setZoom(75)

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-full h-full max-w-7xl max-h-[95vh] overflow-hidden flex">
        {/* Properties Sidebar */}
        {showProperties && (
          <div className="w-64 border-r bg-gray-50 p-4 overflow-y-auto">
            <h4 className="font-semibold mb-4 text-gray-800">Document Properties</h4>
            <div className="space-y-3">
              <div>
                <label className="text-sm font-medium text-gray-600">Pages</label>
                <p className="text-sm text-gray-800">{totalPages}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-600">Words</label>
                <p className="text-sm text-gray-800">{wordCount.toLocaleString()}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-600">Characters</label>
                <p className="text-sm text-gray-800">{charCount.toLocaleString()}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-600">Layout</label>
                <p className="text-sm text-gray-800 capitalize">{layoutMode} Layout</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-600">Zoom</label>
                <p className="text-sm text-gray-800">{zoom}%</p>
              </div>
            </div>
          </div>
        )}

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header Toolbar */}
        <div className="flex items-center justify-between p-3 border-b bg-gray-50">
          <div className="flex items-center gap-4">
            <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <FileText className="w-4 h-4" />
              <span>Page {currentPage} of {totalPages}</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Layout Toggle */}
            <div className="flex items-center gap-1 border rounded px-2 py-1">
              <button
                onClick={() => setLayoutMode('web')}
                className={`px-3 py-1 text-sm rounded ${layoutMode === 'web' ? 'bg-blue-500 text-white' : 'hover:bg-gray-200'}`}
              >
                Web Layout
              </button>
              <button
                onClick={() => setLayoutMode('print')}
                className={`px-3 py-1 text-sm rounded ${layoutMode === 'print' ? 'bg-blue-500 text-white' : 'hover:bg-gray-200'}`}
              >
                Print Layout
              </button>
            </div>

            {/* Zoom Controls */}
            <div className="flex items-center gap-1 border rounded px-2 py-1">
              <button onClick={zoomOut} className="p-1 hover:bg-gray-200 rounded">
                <ZoomOut className="w-4 h-4" />
              </button>
              <span className="text-sm px-2 min-w-[3rem] text-center">{zoom}%</span>
              <button onClick={zoomIn} className="p-1 hover:bg-gray-200 rounded">
                <ZoomIn className="w-4 h-4" />
              </button>
            </div>

            <button onClick={fitToWidth} className="px-3 py-1 text-sm hover:bg-gray-200 rounded border">
              Fit Width
            </button>
            <button onClick={fitToPage} className="px-3 py-1 text-sm hover:bg-gray-200 rounded border">
              Fit Page
            </button>

            <button
              onClick={() => setShowProperties(!showProperties)}
              className={`px-3 py-1 text-sm rounded border ${showProperties ? 'bg-blue-500 text-white' : 'hover:bg-gray-200'}`}
            >
              Properties
            </button>

            {showEditButton && onEdit && (
              <Button variant="outline" onClick={onEdit}>
                <Edit className="w-4 h-4 mr-1" />
                Edit
              </Button>
            )}

            <Button variant="outline" onClick={onClose}>
              <X className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Page Navigation */}
        <div className="flex items-center justify-center p-2 border-b bg-gray-50">
          <div className="flex items-center gap-2">
            <button
              onClick={() => goToPage(currentPage - 1)}
              disabled={currentPage <= 1}
              className="p-1 hover:bg-gray-200 rounded disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>

            {/* Page Thumbnails (simplified) */}
            <div className="flex gap-1">
              {Array.from({ length: Math.min(totalPages, 10) }, (_, i) => i + 1).map(pageNum => (
                <button
                  key={pageNum}
                  onClick={() => goToPage(pageNum)}
                  className={`w-8 h-8 text-xs rounded border ${
                    pageNum === currentPage
                      ? 'bg-blue-500 text-white border-blue-500'
                      : 'hover:bg-gray-200 border-gray-300'
                  }`}
                >
                  {pageNum}
                </button>
              ))}
              {totalPages > 10 && (
                <span className="px-2 text-gray-500">...</span>
              )}
            </div>

            <button
              onClick={() => goToPage(currentPage + 1)}
              disabled={currentPage >= totalPages}
              className="p-1 hover:bg-gray-200 rounded disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Document Content */}
        <div className="flex-1 overflow-auto bg-gray-100 p-8">
          <div className="flex justify-center">
            <div
              className="bg-white shadow-2xl relative"
              style={{
                width: `${595 * (zoom / 100)}px`,
                minHeight: `${842 * (zoom / 100)}px`,
                transform: `scale(${zoom / 100})`,
                transformOrigin: 'top center',
                marginBottom: `${100 * (zoom / 100)}px`,
                border: '1px solid #e5e5e5'
              }}
            >
              {/* Ruler/Margin Guides */}
              <div className="absolute top-0 left-0 right-0 h-6 bg-gray-100 border-b border-gray-300 flex items-center px-4">
                <div className="flex text-xs text-gray-500">
                  <span className="w-16">1"</span>
                  <span className="w-16">2"</span>
                  <span className="w-16">3"</span>
                  <span className="w-16">4"</span>
                  <span className="w-16">5"</span>
                  <span className="w-16">6"</span>
                </div>
              </div>

              {/* Page Header Margin */}
              <div className="h-16 bg-white border-b border-gray-200 mt-6"></div>

              {/* Content Area */}
              <div
                ref={contentRef}
                className="px-16 py-8 min-h-[700px] word-preview-content"
                style={{
                  fontFamily: "'Times New Roman', serif",
                  fontSize: '12pt',
                  lineHeight: '1.6',
                  color: '#000000'
                }}
                dangerouslySetInnerHTML={{
                  __html: `
                    <style>
                      .word-preview-content {
                        margin-left: 1.25in;
                        margin-right: 1.25in;
                      }
                      .word-preview-content h1, .word-preview-content h2, .word-preview-content h3,
                      .word-preview-content h4, .word-preview-content h5, .word-preview-content h6 {
                        color: #2c3e50;
                        margin-top: 24px;
                        margin-bottom: 12px;
                        font-weight: bold;
                        page-break-after: avoid;
                      }
                      .word-preview-content h1 {
                        font-size: 24pt;
                        border-bottom: 2px solid #3498db;
                        padding-bottom: 8px;
                        page-break-after: always;
                      }
                      .word-preview-content h2 {
                        font-size: 18pt;
                        border-bottom: 1px solid #bdc3c7;
                        padding-bottom: 4px;
                      }
                      .word-preview-content h3 { font-size: 14pt; }
                      .word-preview-content h4 { font-size: 12pt; }
                      .word-preview-content p {
                        margin: 8px 0;
                        text-align: justify;
                        text-indent: 1cm;
                        orphans: 2;
                        widows: 2;
                      }
                      .word-preview-content ul, .word-preview-content ol {
                        margin: 10px 0;
                        padding-left: 30px;
                      }
                      .word-preview-content blockquote {
                        margin: 20px 0;
                        padding: 10px 20px;
                        border-left: 4px solid #ccc;
                        background: #f9f9f9;
                      }
                      .word-preview-content table {
                        border-collapse: collapse;
                        width: 100%;
                        margin: 10px 0;
                        page-break-inside: avoid;
                      }
                      .word-preview-content th, .word-preview-content td {
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                      }
                      .word-preview-content th {
                        background-color: #f2f2f2;
                      }
                      .word-preview-content .page-break {
                        page-break-before: always;
                      }
                    </style>
                    ${currentPageContent}
                  `
                }}
              />

              {/* Page Footer Margin */}
              <div className="absolute bottom-0 left-0 right-0 h-16 bg-white border-t border-gray-200 flex items-center justify-center">
                <span className="text-xs text-gray-500">Page {currentPage} of {totalPages}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Status Bar */}
        <div className="flex items-center justify-between px-4 py-2 border-t bg-gray-50 text-sm text-gray-600">
          <div>Zoom: {zoom}% | Layout: {layoutMode}</div>
          <div>Ready</div>
        </div>
        </div>
      </div>
    </div>
  )
}