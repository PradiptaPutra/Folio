import axios, { AxiosError } from 'axios'

// @ts-ignore - ImportMeta.env is valid in Vite
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ============================================================================
// Type Definitions
// ============================================================================

export interface SemanticElement {
  type: 'chapter' | 'subchapter' | 'subsubchapter' | 'paragraph' | 'list' | 'table_caption' | 'figure_caption' | 'equation' | 'bibliography_entry' | 'appendix'
  text: string
  confidence: number
  metadata?: Record<string, any>
}

export interface SemanticParseResult {
  elements: SemanticElement[]
  warnings: string[]
  overall_confidence: number
  error?: string
}

export interface FrontMatterClassification {
  category: 'title_page' | 'approval_page' | 'originality_statement' | 'dedication' | 'motto' | 'preface' | 'abstract_id' | 'abstract_en' | 'glossary' | 'table_of_contents' | 'list_of_tables' | 'list_of_figures' | 'unknown'
  confidence: number
  reason: string
}

export interface StyleInference {
  semantic_role: 'chapter_title' | 'subchapter_title' | 'body_paragraph' | 'caption' | 'bibliography' | 'front_matter_heading' | 'unknown'
  confidence: number
  reasoning: string
  recommendations: string[]
}

export interface QAExplanation {
  summary: string
  groups: {
    critical: Array<{ location: string; explanation: string; impact: string }>
    warning: Array<{ location: string; explanation: string; impact: string }>
    info: Array<{ location: string; explanation: string; impact: string }>
  }
  overall_assessment: string
  recommendations: string[]
}

export interface FidelityValidation {
  diffs: Record<string, any>
  fidelity_score: number
  is_valid: boolean
}

export interface Phase {
  name: string
  description: string
  implemented: boolean
}

export interface EnforcementStatus {
  status: 'available' | 'unavailable'
  version: string
  phases: Record<string, Phase>
  implementation: {
    technology: string
    version: string
  }
}

export interface EnforcementResults {
  phase_3_1_merges: number
  phase_3_2_paragraphs: number
  phase_3_3_toc_inserted: boolean
  phase_3_4_headings: Record<string, number>
  phase_3_5_page_breaks: number
  phase_3_5_numbering_reset: boolean
}

export interface EnforcementResponse {
  status: 'success' | 'error'
  message: string
  file: string
  results: EnforcementResults
  timestamp?: string
}

export interface FrontmatterData {
  // Basic Information
  judul?: string
  penulis?: string
  nim?: string

  // Academic Information
  universitas?: string
  fakultas?: string
  program_studi?: string
  jurusan?: string

  // Academic Supervision
  dosen_pembimbing?: string
  dosen_pembimbing2?: string
  penguji1?: string
  penguji2?: string

  // Location and Time
  kota?: string
  tahun?: number | string

  // Content
  abstrak_id?: string
  abstrak_teks?: string
  abstrak_en_teks?: string
  kata_kunci?: string

  // Optional advanced fields
  gelar?: string
  tanggal_sidang?: string
  nomor_skripsi?: string
}

export interface TemplateAnalysis {
  metadata: {
    university: string
    faculty?: string
    program?: string
    version: string
    standard: string
    converted_from?: string
    source_file?: string
  }
  document_properties: {
    page_size: { width: number; height: number }
    margins: { top: number; bottom: number; left: number; right: number }
    orientation: string
  }
  typography: {
    fonts: { primary: string; secondary?: string; monospace?: string }
    sizes: Record<string, number>
    line_spacing: number
    indentation: { first_line: number; hanging?: number }
  }
  structure: {
    front_matter: Array<{ type: string; required: boolean; order?: number }>
    main_content: {
      chapter_pattern: string
      heading_styles: Record<string, any>
    }
    back_matter: Array<{ type: string; required: boolean }>
  }
  validation_rules: {
    required_sections: string[]
    font_restrictions: string[]
    size_limits: Record<string, number>
  }
}

export interface ThesisGenerationOptions {
  use_ai: boolean
  include_frontmatter: boolean
  api_key?: string
  template_format?: 'docx' | 'json' | 'xml'
}

export interface ThesisGenerationResponse {
  status: 'success' | 'error'
  message: string
  output_file?: string
  file_size?: number
  report?: {
    template_analysis?: TemplateAnalysis
    quality_score?: number
    compliance_score?: number
    recommendations?: string[]
  }
  error_details?: string
}

export interface TemplateConversionResponse {
  status: 'success' | 'error'
  message: string
  template_data?: TemplateAnalysis
  output_file?: string
  analysis_summary?: string
}

export interface ApiError {
  status: number
  message: string
  detail?: string
}

// ============================================================================
// API Functions - AI & Analysis
// ============================================================================

/**
 * Parse raw text into semantic structure using AI
 */
export async function parseTextSemantics(text: string): Promise<SemanticParseResult> {
  try {
    const response = await apiClient.post<SemanticParseResult>('/ai/parse-text', {
      text,
    })
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError
    throw {
      status: axiosError.response?.status || 500,
      message: 'Failed to parse text',
      detail: axiosError.message,
    } as ApiError
  }
}

/**
 * Classify front matter blocks using AI
 */
export async function classifyFrontMatter(blocks: string[]): Promise<FrontMatterClassification[]> {
  try {
    const response = await apiClient.post<FrontMatterClassification[]>('/ai/classify-frontmatter', {
      blocks,
    })
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError
    throw {
      status: axiosError.response?.status || 500,
      message: 'Failed to classify front matter',
      detail: axiosError.message,
    } as ApiError
  }
}

/**
 * Infer style intent from template analysis
 */
export async function inferStyleIntent(styleData: Record<string, any>): Promise<StyleInference> {
  try {
    const response = await apiClient.post<StyleInference>('/ai/infer-style', {
      style_data: styleData,
    })
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError
    throw {
      status: axiosError.response?.status || 500,
      message: 'Failed to infer style',
      detail: axiosError.message,
    } as ApiError
  }
}

/**
 * Generate abstract in Indonesian
 */
export async function generateAbstractId(params: {
  title: string
  objectives: string
  methods: string
  results: string
}): Promise<{ abstract: string }> {
  try {
    const response = await apiClient.post<{ abstract: string }>('/ai/generate-abstract-id', params)
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError
    throw {
      status: axiosError.response?.status || 500,
      message: 'Failed to generate abstract',
      detail: axiosError.message,
    } as ApiError
  }
}

/**
 * Generate abstract in English
 */
export async function generateAbstractEn(params: {
  title: string
  objectives: string
  methods: string
  results: string
}): Promise<{ abstract: string }> {
  try {
    const response = await apiClient.post<{ abstract: string }>('/ai/generate-abstract-en', params)
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError
    throw {
      status: axiosError.response?.status || 500,
      message: 'Failed to generate abstract',
      detail: axiosError.message,
    } as ApiError
  }
}

/**
 * Generate preface
 */
export async function generatePreface(params: {
  title: string
  author: string
  institution: string
  thesis_focus: string
}): Promise<{ preface: string }> {
  try {
    const response = await apiClient.post<{ preface: string }>('/ai/generate-preface', params)
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError
    throw {
      status: axiosError.response?.status || 500,
      message: 'Failed to generate preface',
      detail: axiosError.message,
    } as ApiError
  }
}

// ============================================================================
// API Functions - Document Generation & Validation
// ============================================================================

// ============================================================================
// API Functions
// ============================================================================

/**
 * Get enforcement system status and available phases
 */
export async function getEnforcementStatus(): Promise<EnforcementStatus> {
  try {
    const response = await apiClient.get<EnforcementStatus>('/enforcement-status')
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError
    throw {
      status: axiosError.response?.status || 500,
      message: 'Failed to get enforcement status',
      detail: axiosError.message,
    } as ApiError
  }
}

/**
 * Validate template and get metadata
 */
export async function validateTemplate(templateFile: File): Promise<{
  status: string
  message: string
  filename: string
  styles: Record<string, any>
  margins: Record<string, any>
}> {
  try {
    const formData = new FormData()
    formData.append('file', templateFile)

    const response = await apiClient.post(
      '/validate-template',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError
    throw {
      status: axiosError.response?.status || 500,
      message: 'Failed to validate template',
      detail: axiosError.message,
    } as ApiError
  }
}

/**
 * Validate output document fidelity
 */
export async function validateFidelity(templatePath: string, outputPath: string): Promise<FidelityValidation> {
  try {
    const response = await apiClient.post<FidelityValidation>('/validate-fidelity', {
      template_path: templatePath,
      output_path: outputPath,
    })
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError
    throw {
      status: axiosError.response?.status || 500,
      message: 'Failed to validate fidelity',
      detail: axiosError.message,
    } as ApiError
  }
}

/**
 * Get QA explanation of changes
 */
export async function getQAExplanation(templatePath: string, outputPath: string): Promise<QAExplanation> {
  try {
    const response = await apiClient.post<QAExplanation>('/qa-explain', {
      template_path: templatePath,
      output_path: outputPath,
    })
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError
    throw {
      status: axiosError.response?.status || 500,
      message: 'Failed to get QA explanation',
      detail: axiosError.message,
    } as ApiError
  }
}

/**
 * Download the processed file from blob
 */
export function downloadFile(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

/**
 * Generate a formatted document from template + content - NOW CREATES COMPLETE THESIS!
 * Uses AI semantic analysis to intelligently structure document.
 * Returns the complete, professionally-structured thesis DOCX file as a blob
 */
export async function generateFromTemplate(
  templateFile: File,
  rawText: string,
  frontmatterData?: FrontmatterData,
  includeFrontmatter: boolean = false,
  useAIAnalysis: boolean = true
): Promise<{ filename: string; file_size: number }> {
  try {
    const textFile = new File([rawText], 'content.txt', { type: 'text/plain' })

    const formData = new FormData()
    formData.append('template_file', templateFile)
    formData.append('content_file', textFile)
    formData.append('include_frontmatter', String(includeFrontmatter))
    formData.append('use_ai_analysis', String(useAIAnalysis))

    if (includeFrontmatter && frontmatterData) {
      // Basic information
      formData.append('title', frontmatterData.judul || '')
      formData.append('author', frontmatterData.penulis || '')
      formData.append('nim', frontmatterData.nim || '')

      // Academic information
      formData.append('university', frontmatterData.universitas || '')
      formData.append('faculty', frontmatterData.fakultas || '')
      formData.append('program', frontmatterData.program_studi || '')
      formData.append('department', frontmatterData.jurusan || '')

      // Academic supervision
      formData.append('supervisor1', frontmatterData.dosen_pembimbing || '')
      formData.append('supervisor2', frontmatterData.dosen_pembimbing2 || '')
      formData.append('examiner1', frontmatterData.penguji1 || '')
      formData.append('examiner2', frontmatterData.penguji2 || '')

      // Location and time
      formData.append('city', frontmatterData.kota || '')
      formData.append('year', String(frontmatterData.tahun || ''))

      // Content
      formData.append('abstract_id', frontmatterData.abstrak_teks || '')
      formData.append('abstract_en', frontmatterData.abstrak_en_teks || '')
      formData.append('keywords', frontmatterData.kata_kunci || '')

      // Optional advanced fields
      formData.append('degree', frontmatterData.gelar || '')
      formData.append('defense_date', frontmatterData.tanggal_sidang || '')
      formData.append('thesis_number', frontmatterData.nomor_skripsi || '')

      // Legacy compatibility
      formData.append('judul', frontmatterData.judul || '')
      formData.append('penulis', frontmatterData.penulis || '')
      formData.append('universitas', frontmatterData.universitas || '')
      formData.append('dosen_pembimbing', frontmatterData.dosen_pembimbing || 'Nama Dosen Pembimbing')
      formData.append('abstrak_id', frontmatterData.abstrak_id || '')
      formData.append('abstrak_teks', frontmatterData.abstrak_teks || '')
      formData.append('abstrak_en_teks', frontmatterData.abstrak_en_teks || '')
      formData.append('kata_kunci', frontmatterData.kata_kunci || '')
    }

    const response = await apiClient.post('/generate', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    return response.data
  } catch (error) {
    const axiosError = error as AxiosError
    throw {
      status: axiosError.response?.status || 500,
      message: 'Failed to generate document',
      detail: axiosError.message,
    } as ApiError
  }
}

/**
 * Download a generated document
 */
export async function downloadGeneratedDocument(filename: string): Promise<Blob> {
  try {
    const response = await apiClient.get(`/download/${filename}`, {
      responseType: 'blob',
    })
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError
    throw {
      status: axiosError.response?.status || 500,
      message: 'Failed to download document',
      detail: axiosError.message,
    } as ApiError
  }
}

// ============================================================================
// API Functions - Universal Formatter
// ============================================================================

export interface TemplateAnalysis {
  status: string
  analysis: {
    margins: Record<string, number>
    front_matter_sections: string[]
    formatting_rules: Record<string, any>
    styles: Record<string, any>
    heading_hierarchy: Record<string, any>
  }
}

export interface ContentExtraction {
  status: string
  sections: Array<{
    title: string
    level: number
    content: string[]
  }>
  section_count: number
}

export interface MergeReport {
  status: string
  message: string
  filename: string
  merge_report: {
    sections_merged: number
    placeholders_replaced: number
    auto_generated_sections: string[]
    warnings: string[]
    timestamp: string
  }
}

/**
 * Analyze a DOCX template to detect structure, styles, and formatting rules
 */
export async function analyzeTemplate(templateFile: File): Promise<TemplateAnalysis> {
  try {
    const formData = new FormData()
    formData.append('file', templateFile)

    const response = await apiClient.post<TemplateAnalysis>(
      '/universal-formatter/analyze-template',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError
    throw {
      status: axiosError.response?.status || 500,
      message: 'Failed to analyze template',
      detail: axiosError.message,
    } as ApiError
  }
}

/**
 * Extract content from DOCX or TXT file
 */
export async function extractContent(contentFile: File): Promise<ContentExtraction> {
  try {
    const formData = new FormData()
    formData.append('file', contentFile)

    const response = await apiClient.post<ContentExtraction>(
      '/universal-formatter/extract-content',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError
    throw {
      status: axiosError.response?.status || 500,
      message: 'Failed to extract content',
      detail: axiosError.message,
    } as ApiError
  }
}

/**
 * Format thesis with universal formatter
 * Works with any university template
 */
export async function formatThesis(
  templateFile: File,
  contentFile: File,
  userData: {
    title: string
    author: string
    nim: string
    advisor: string
    institution: string
    date: string
  }
): Promise<{ blob: Blob; filename: string }> {
  try {
    const formData = new FormData()
    formData.append('template_file', templateFile)
    formData.append('content_file', contentFile)
    formData.append('title', userData.title)
    formData.append('author', userData.author)
    formData.append('nim', userData.nim)
    formData.append('advisor', userData.advisor)
    formData.append('institution', userData.institution)
    formData.append('date', userData.date)

    const response = await apiClient.post(
      '/universal-formatter/format-thesis',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        responseType: 'blob',
      }
    )

    const contentDisposition = response.headers['content-disposition']
    let filename = 'formatted_thesis.docx'

    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/)
      if (filenameMatch) {
        filename = filenameMatch[1]
      }
    }

    return {
      blob: response.data as Blob,
      filename,
    }
  } catch (error) {
    const axiosError = error as AxiosError
    console.error('Format thesis error:', axiosError)
    throw {
      status: axiosError.response?.status || 500,
      message: 'Failed to format thesis',
      detail: axiosError.response?.statusText || axiosError.message,
    } as ApiError
  }
}

/**
 * Get universal formatter information
 */
export async function getFormatterInfo(): Promise<{ status: string; message: string; capabilities: string[] }> {
  try {
    const response = await apiClient.get('/universal-formatter/info')
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError
    throw {
      status: axiosError.response?.status || 500,
      message: 'Failed to get formatter info',
      detail: axiosError.message,
    } as ApiError
  }
}

/**
 * Validate semantic structure of document content
 */
export async function validateSemanticStructure(
  contentFile: File,
  useAI: boolean = true
): Promise<{
  status: string
  validation: {
    status: string
    issues: string[]
    warnings: string[]
    suggestions: string[]
  }
  summary: {
    total_sections: number
    ai_analyzed_sections: number
    rule_based_sections: number
    ai_available: boolean
    semantic_types: string[]
    average_confidence: number
  }
  sections: Array<{
    title: string
    type: string
    level: number
    ai_analyzed: boolean
    confidence: number
    length: number
  }>
}> {
  try {
    const formData = new FormData()
    formData.append('content_file', contentFile)
    formData.append('use_ai', String(useAI))

    const response = await apiClient.post(
      '/validate-semantic-structure',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError
    throw {
      status: axiosError.response?.status || 500,
      message: 'Failed to validate semantic structure',
      detail: axiosError.message,
    } as ApiError
  }
}

/**
 * Check if AI semantic analysis is available
 */
export async function getAIAnalysisStatus(): Promise<{
  ai_available: boolean
  semantic_parser_available: boolean
  capabilities: string[]
  error?: string
}> {
  try {
    const response = await apiClient.get('/ai-analysis-status')
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError
    return {
      ai_available: false,
      semantic_parser_available: false,
      capabilities: [],
      error: axiosError.message,
    }
  }
}

/**
 * Generate HTML preview of a generated document
 */
export async function previewGeneratedDocument(filename: string): Promise<{ html_content: string }> {
  try {
    const response = await apiClient.get(`/preview-generated/${filename}`)
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError
    throw {
      status: axiosError.response?.status || 500,
      message: 'Failed to generate document preview',
      detail: axiosError.message,
    } as ApiError
  }
}

/**
 * Save edited HTML content
 */
export async function saveEditedContent(content: string): Promise<{ content_id: string }> {
  try {
    const formData = new FormData()
    formData.append('content', content)

    const response = await apiClient.post('/save-edited-content', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError
    throw {
      status: axiosError.response?.status || 500,
      message: 'Failed to save edited content',
      detail: axiosError.message,
    } as ApiError
  }
}

/**
 * Upload and analyze university template for perfect formatting
 */
export async function uploadTemplate(templateFile: File): Promise<TemplateAnalysis> {
  try {
    const formData = new FormData()
    formData.append('file', templateFile)

    const response = await apiClient.post<TemplateAnalysis>('/template/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError
    throw {
      status: axiosError.response?.status || 500,
      message: 'Failed to analyze template',
      detail: axiosError.message,
    } as ApiError
  }
}

/**
 * Convert DOCX template to structured JSON format
 */
export async function convertTemplate(templateFile: File, format: 'json' | 'xml' = 'json'): Promise<TemplateConversionResponse> {
  try {
    const formData = new FormData()
    formData.append('file', templateFile)
    formData.append('format', format)

    const response = await apiClient.post<TemplateConversionResponse>('/template/convert', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError
    throw {
      status: axiosError.response?.status || 500,
      message: 'Failed to convert template',
      detail: axiosError.message,
    } as ApiError
  }
}

/**
 * Generate thesis with AI enhancement and perfect template adaptation
 */
export async function generatePerfectThesis(
  templateFile: File,
  contentFile: File,
  userData: FrontmatterData,
  options: ThesisGenerationOptions = { use_ai: true, include_frontmatter: true }
): Promise<ThesisGenerationResponse> {
  try {
    const formData = new FormData()
    formData.append('template', templateFile)
    formData.append('content', contentFile)
    formData.append('user_data', JSON.stringify(userData))
    formData.append('options', JSON.stringify(options))

    const response = await apiClient.post<ThesisGenerationResponse>('/thesis/generate-perfect', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError
    throw {
      status: axiosError.response?.status || 500,
      message: 'Failed to generate perfect thesis',
      detail: axiosError.message,
    } as ApiError
  }
}

export default apiClient

