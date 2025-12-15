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
  judul?: string
  penulis?: string
  nim?: string
  universitas?: string
  tahun?: number | string
  abstrak_id?: string
  abstrak_teks?: string
  abstrak_en_teks?: string
  kata_kunci?: string
}

export interface ApiError {
  status: number
  message: string
  detail?: string
}

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
 * Upload a document and enforce it with optional front-matter
 * Returns the processed DOCX file as a blob
 * 
 * This calls the unified /generate endpoint with file enforcement workflow
 */
export async function enforceDocument(
  file: File,
  includeFrontmatter: boolean,
  frontmatterData?: FrontmatterData
): Promise<{ blob: Blob; filename: string }> {
  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('include_frontmatter', String(includeFrontmatter))

    // Always send all form fields with defaults
    formData.append('judul', frontmatterData?.judul || 'JUDUL SKRIPSI')
    formData.append('penulis', frontmatterData?.penulis || 'Nama Penulis')
    formData.append('nim', frontmatterData?.nim || 'NIM')
    formData.append('universitas', frontmatterData?.universitas || 'Universitas')
    formData.append('tahun', String(frontmatterData?.tahun || new Date().getFullYear()))
    formData.append('abstrak_id', frontmatterData?.abstrak_id || 'ABSTRAK')
    formData.append('abstrak_teks', frontmatterData?.abstrak_teks || 'Isi abstrak di sini.')
    formData.append('abstrak_en_teks', frontmatterData?.abstrak_en_teks || 'Abstract content here.')
    formData.append('kata_kunci', frontmatterData?.kata_kunci || 'keyword1, keyword2')

    const response = await apiClient.post(
      '/generate',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        responseType: 'blob',
      }
    )

    // Extract filename from content-disposition header if available
    const contentDisposition = response.headers['content-disposition']
    let filename = file.name.replace('.docx', '_enforced.docx')
    
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
    console.error('Enforce document error:', axiosError)
    
    // Try to extract error detail from response blob
    let errorDetail = 'Unprocessable Entity'
    if (axiosError.response?.data instanceof Blob) {
      try {
        const text = await (axiosError.response.data as Blob).text()
        console.error('Backend error response:', text)
        errorDetail = text
      } catch (e) {
        console.error('Could not parse error blob')
      }
    }
    
    throw {
      status: axiosError.response?.status || 500,
      message: 'Failed to enforce document',
      detail: errorDetail,
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
 * Validate a template DOCX file
 * The template will be uploaded directly to /generate along with content
 */
export async function uploadTemplate(templateFile: File): Promise<{
  reference_docx: string
  message: string
}> {
  // Validate it's a DOCX file
  if (!templateFile.name.endsWith('.docx')) {
    throw {
      status: 400,
      message: 'Invalid template file',
      detail: 'Template must be a .docx file',
    } as ApiError
  }

  if (templateFile.size > 50 * 1024 * 1024) { // 50MB limit
    throw {
      status: 400,
      message: 'Template file too large',
      detail: 'Template must be less than 50MB',
    } as ApiError
  }

  return {
    reference_docx: templateFile.name,
    message: 'Template validated - ready to use',
  }
}

/**
 * Generate a formatted document from raw text using a template
 * Supports two modes:
 * 1. Upload new template file + raw text
 * 2. Use existing template reference + raw text
 * Returns the generated DOCX file as a blob
 */
export async function generateFromText(
  rawText: string,
  templateFile?: File,
  templateReference?: string,
  outputFormat: string = 'docx',
  contentFile?: File,
  frontmatterData?: FrontmatterData,
  includeFrontmatter: boolean = false
): Promise<{ blob: Blob; filename: string }> {
  try {
    // Use uploaded content file if available, otherwise create from text
    const textFile = contentFile || new File([rawText], 'content.txt', { type: 'text/plain' })

    const formData = new FormData()
    
    // Add template (either file or reference)
    if (templateFile) {
      formData.append('template_file', templateFile)
    } else if (templateReference) {
      formData.append('reference_name', templateReference)
    } else {
      throw new Error('Either templateFile or templateReference must be provided')
    }
    
    formData.append('content_file', textFile)
    formData.append('output_format', outputFormat)
    formData.append('include_frontmatter', String(includeFrontmatter))

    if (includeFrontmatter && frontmatterData) {
        formData.append('judul', frontmatterData.judul || '')
        formData.append('penulis', frontmatterData.penulis || '')
        formData.append('nim', frontmatterData.nim || '')
        formData.append('universitas', frontmatterData.universitas || '')
        formData.append('tahun', String(frontmatterData.tahun || ''))
        formData.append('abstrak_id', frontmatterData.abstrak_id || 'ABSTRAK')
        formData.append('abstrak_teks', frontmatterData.abstrak_teks || '')
        formData.append('abstrak_en_teks', frontmatterData.abstrak_en_teks || '')
        formData.append('kata_kunci', frontmatterData.kata_kunci || '')
    }

    const response = await apiClient.post(
      '/generate',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        responseType: 'blob',
      }
    )

    // Extract filename from content-disposition header if available
    const contentDisposition = response.headers['content-disposition']
    let filename = `formatted.${outputFormat.toLowerCase()}`

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
    console.error('Generate document error:', axiosError)
    throw {
      status: axiosError.response?.status || 500,
      message: 'Failed to generate formatted document',
      detail: axiosError.response?.statusText || axiosError.message,
    } as ApiError
  }
}

export default apiClient
