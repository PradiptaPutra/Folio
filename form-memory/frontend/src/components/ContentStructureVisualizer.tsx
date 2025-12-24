import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { FileText, Book, BookOpen, CheckCircle, AlertCircle } from 'lucide-react'

interface ContentStructure {
  title: string
  content: string[]
  level: number
  type: string
  confidence?: number
}

interface ContentStructureVisualizerProps {
  sections: ContentStructure[]
  totalWordCount?: number
  aiConfidence?: number
  missingSections?: string[]
}

export function ContentStructureVisualizer({
  sections,
  totalWordCount = 0,
  aiConfidence = 0,
  missingSections = []
}: ContentStructureVisualizerProps) {
  const getSectionIcon = (type: string) => {
    switch (type) {
      case 'chapter':
        return <Book className="w-4 h-4" />
      case 'section':
        return <BookOpen className="w-4 h-4" />
      default:
        return <FileText className="w-4 h-4" />
    }
  }

  const getConfidenceColor = (confidence?: number) => {
    if (!confidence) return 'bg-gray-100'
    if (confidence >= 0.8) return 'bg-green-100 text-green-800'
    if (confidence >= 0.6) return 'bg-yellow-100 text-yellow-800'
    return 'bg-red-100 text-red-800'
  }

  const getSectionPreview = (content: string[]) => {
    const preview = content.slice(0, 2).join(' ').substring(0, 100)
    return preview + (content.length > 0 && content.join(' ').length > 100 ? '...' : '')
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="w-5 h-5" />
          Content Structure Analysis
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Summary Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{sections.length}</div>
            <div className="text-sm text-gray-600">Sections</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{totalWordCount}</div>
            <div className="text-sm text-gray-600">Words</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {aiConfidence > 0 ? `${Math.round(aiConfidence * 100)}%` : 'N/A'}
            </div>
            <div className="text-sm text-gray-600">AI Confidence</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">{missingSections.length}</div>
            <div className="text-sm text-gray-600">Missing</div>
          </div>
        </div>

        {/* Section List */}
        <div className="space-y-3">
          <h3 className="text-lg font-semibold">Detected Sections</h3>
          {sections.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No sections detected in your content.</p>
              <p className="text-sm">Try adding chapter headings like "BAB I:", "BAB II:", etc.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {sections.map((section, index) => (
                <div
                  key={index}
                  className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-3">
                      {getSectionIcon(section.type)}
                      <div>
                        <h4 className="font-semibold text-sm">{section.title}</h4>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge variant="outline" className="text-xs">
                            {section.type}
                          </Badge>
                          {section.confidence && (
                            <Badge className={`text-xs ${getConfidenceColor(section.confidence)}`}>
                              {Math.round(section.confidence * 100)}% confidence
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="text-right text-sm text-gray-500">
                      <div>{section.content.length} paragraphs</div>
                      <div>Level {section.level}</div>
                    </div>
                  </div>

                  {section.content.length > 0 && (
                    <div className="mt-3 p-3 bg-gray-50 rounded text-sm text-gray-700">
                      <div className="font-medium mb-1">Preview:</div>
                      <div className="italic">"{getSectionPreview(section.content)}"</div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Missing Sections Alert */}
        {missingSections.length > 0 && (
          <div className="border border-orange-200 bg-orange-50 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-orange-600 mt-0.5" />
              <div>
                <h4 className="font-semibold text-orange-800">Missing Sections Detected</h4>
                <p className="text-sm text-orange-700 mt-1">
                  Consider adding these standard thesis sections:
                </p>
                <div className="flex flex-wrap gap-2 mt-2">
                  {missingSections.map((section, index) => (
                    <Badge key={index} variant="outline" className="text-orange-700 border-orange-300">
                      {section}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Success Message */}
        {sections.length > 0 && missingSections.length === 0 && (
          <div className="border border-green-200 bg-green-50 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
              <div>
                <h4 className="font-semibold text-green-800">Content Structure Complete</h4>
                <p className="text-sm text-green-700 mt-1">
                  Your content has been successfully analyzed and organized into {sections.length} sections.
                  The document is ready for generation!
                </p>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}