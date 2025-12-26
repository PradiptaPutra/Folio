import { Check, Eye, Download, FileText, Edit } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useState } from 'react'
import { WordStylePreview } from './WordStylePreview'

interface SuccessViewProps {
  fileName: string
  onDownload: () => void
  onFormatAnother: () => void
  onPreview?: () => void
  previewContent?: string | null
  onEdit?: () => void
}

export function SuccessView({
  fileName,
  onDownload,
  onFormatAnother,
  onPreview,
  previewContent,
  onEdit,
}: SuccessViewProps) {
  const [showPreview, setShowPreview] = useState(false)

  const handlePreview = () => {
    if (onPreview) {
      onPreview()
    }
    setShowPreview(true)
  }

  return (
    <div className="w-full max-w-2xl mx-auto py-16 text-center space-y-8">
      {/* Success Badge */}
      <div className="inline-flex items-center justify-center">
        <div className="w-24 h-24 rounded-full bg-primary/10 flex items-center justify-center">
          <Check className="w-12 h-12 text-primary" strokeWidth={1.5} />
        </div>
      </div>

      {/* Heading */}
      <div className="space-y-3">
        <h2 className="text-display">Your thesis is ready</h2>
        <p className="text-body-lg text-muted-foreground">
          Your document has been formatted with your university's template and is ready to download.
        </p>
      </div>

      {/* File Info */}
      <div className="p-6 bg-card border border-border rounded">
        <p className="text-sm text-muted-foreground mb-2">File generated:</p>
        <p className="font-semibold font-mono text-sm break-all">{fileName}</p>
      </div>

      {/* Actions */}
      <div className="flex gap-4 justify-center flex-wrap">
        <Button variant="hero" onClick={onDownload} className="flex items-center gap-2">
          <Download className="w-4 h-4" />
          Download DOCX
        </Button>
        {onPreview && (
          <Button variant="outline" onClick={handlePreview} className="flex items-center gap-2">
            <Eye className="w-4 h-4" />
            Preview Document
          </Button>
        )}
        {onEdit && (
          <Button variant="outline" onClick={onEdit} className="flex items-center gap-2">
            <Edit className="w-4 h-4" />
            Edit Document
          </Button>
        )}
        <Button variant="outline" onClick={onFormatAnother}>
          Format Another
        </Button>
      </div>

       {/* Preview Modal */}
       {showPreview && previewContent && (
         <WordStylePreview
           content={previewContent}
           title="Generated Document Preview"
           onClose={() => setShowPreview(false)}
           onEdit={onEdit}
           showEditButton={!!onEdit}
         />
       )}

       {showPreview && !previewContent && (
         <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
           <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
             <div className="flex items-center justify-between p-4 border-b">
               <h3 className="text-lg font-semibold">Document Preview</h3>
               <button
                 onClick={() => setShowPreview(false)}
                 className="text-gray-500 hover:text-gray-700"
               >
                 <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                   <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                 </svg>
               </button>
             </div>
             <div className="p-4">
               <div className="flex items-center justify-center h-[70vh] text-gray-500">
                 <div className="text-center">
                   <FileText className="mx-auto h-16 w-16 text-blue-500" />
                   <h3 className="mt-4 text-lg font-medium text-gray-900">Document Preview</h3>
                   <p className="mt-2 text-sm text-gray-600 max-w-md">
                     Your thesis document has been successfully generated and formatted.
                   </p>
                   <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                     <p className="text-sm text-blue-800 font-medium">Ready to Download</p>
                     <p className="mt-1 text-sm text-blue-600">
                       The document is fully formatted with your university's template, including all sections, chapters, and proper formatting.
                     </p>
                   </div>
                   <div className="mt-4 flex justify-center gap-3">
                     <Button onClick={onDownload} className="flex items-center gap-2">
                       <Download className="w-4 h-4" />
                       Download DOCX
                     </Button>
                   </div>
                 </div>
               </div>
             </div>
           </div>
         </div>
       )}
    </div>
  )
}
