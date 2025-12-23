import { useState } from 'react'
import { Upload } from 'lucide-react'
import { cn } from '@/lib/utils'

interface FileUploadProps {
  onFileSelect: (file: File) => void
  accept?: string
  maxSize?: number
  label?: string
  description?: string
}

export function FileUpload({
  onFileSelect,
  accept = '*',
  maxSize,
  label,
  description,
}: FileUploadProps) {
  const [dragOver, setDragOver] = useState(false)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(true)
  }

  const handleDragLeave = () => {
    setDragOver(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const files = e.dataTransfer.files
    if (files.length > 0) {
      const file = files[0]
      if (maxSize && file.size > maxSize) {
        alert(`File size exceeds ${maxSize / 1024 / 1024}MB limit`)
        return
      }
      onFileSelect(file)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.currentTarget.files
    if (files?.length) {
      const file = files[0]
      if (maxSize && file.size > maxSize) {
        alert(`File size exceeds ${maxSize / 1024 / 1024}MB limit`)
        return
      }
      onFileSelect(file)
    }
  }

  return (
    <div className="w-full">
      {label && <label className="block text-sm font-semibold mb-2">{label}</label>}
      
      <label
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={cn(
          'upload-zone',
          'relative p-8 cursor-pointer transition-all duration-200',
          dragOver && 'dragover bg-primary/5 border-primary'
        )}
      >
        <input
          type="file"
          accept={accept}
          onChange={handleInputChange}
          className="hidden"
        />

        <div className="flex flex-col items-center justify-center space-y-3">
          <Upload
            size={32}
            className={cn(
              'transition-colors duration-200',
              dragOver ? 'text-primary' : 'text-muted-foreground'
            )}
          />
          <div className="text-center">
            <p className="font-semibold text-sm">
              {dragOver ? 'Drop your file here' : 'Drag and drop your file here'}
            </p>
            {description && (
              <p className="text-xs text-muted-foreground mt-1">{description}</p>
            )}
          </div>
        </div>
      </label>
    </div>
  )
}
