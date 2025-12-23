interface DetailsFormProps {
  onSubmit: (data: FormData) => void
  isLoading?: boolean
}

interface FormData {
  name: string
  studentId: string
  title: string
  advisor: string
  university: string
  department?: string
}

export function DetailsForm({ onSubmit, isLoading }: DetailsFormProps) {
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const data = {
      name: formData.get('name') as string,
      studentId: formData.get('studentId') as string,
      title: formData.get('title') as string,
      advisor: formData.get('advisor') as string,
      university: formData.get('university') as string,
      department: formData.get('department') as string,
    }
    onSubmit(data)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Name */}
        <div className="space-y-2">
          <label className="block text-sm font-semibold">Full Name *</label>
          <input
            type="text"
            name="name"
            required
            className="w-full px-4 py-3 border border-border rounded bg-background focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
            placeholder="John Doe"
          />
        </div>

        {/* Student ID */}
        <div className="space-y-2">
          <label className="block text-sm font-semibold">Student ID *</label>
          <input
            type="text"
            name="studentId"
            required
            className="w-full px-4 py-3 border border-border rounded bg-background focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
            placeholder="123456789"
          />
        </div>

        {/* Title */}
        <div className="space-y-2 md:col-span-2">
          <label className="block text-sm font-semibold">Thesis Title *</label>
          <input
            type="text"
            name="title"
            required
            className="w-full px-4 py-3 border border-border rounded bg-background focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
            placeholder="Your thesis title here"
          />
        </div>

        {/* Advisor */}
        <div className="space-y-2">
          <label className="block text-sm font-semibold">Thesis Advisor *</label>
          <input
            type="text"
            name="advisor"
            required
            className="w-full px-4 py-3 border border-border rounded bg-background focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
            placeholder="Dr. Jane Smith"
          />
        </div>

        {/* University */}
        <div className="space-y-2">
          <label className="block text-sm font-semibold">University *</label>
          <input
            type="text"
            name="university"
            required
            className="w-full px-4 py-3 border border-border rounded bg-background focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
            placeholder="University Name"
          />
        </div>

        {/* Department */}
        <div className="space-y-2 md:col-span-2">
          <label className="block text-sm font-semibold">Department (optional)</label>
          <input
            type="text"
            name="department"
            className="w-full px-4 py-3 border border-border rounded bg-background focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
            placeholder="Department / Faculty Name"
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="btn-default w-full"
      >
        {isLoading ? 'Processing...' : 'Continue'}
      </button>
    </form>
  )
}
