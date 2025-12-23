import { Check } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface SuccessViewProps {
  fileName: string
  onDownload: () => void
  onFormatAnother: () => void
}

export function SuccessView({
  fileName,
  onDownload,
  onFormatAnother,
}: SuccessViewProps) {
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
      <div className="flex gap-4 justify-center">
        <Button variant="hero" onClick={onDownload}>
          Download DOCX
        </Button>
        <Button variant="outline" onClick={onFormatAnother}>
          Format Another
        </Button>
      </div>
    </div>
  )
}
