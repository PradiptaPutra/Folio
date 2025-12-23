import { useState } from 'react'
import { TemplateGenerator } from '@/components/TemplateGenerator'
import { DocumentUploader } from '@/components/DocumentUploader'
import { StatusPage } from '@/components/StatusPage'
import { Button } from '@/components/ui/button'
import { ArrowRight } from 'lucide-react'

type Page = 'home' | 'generate' | 'enforce' | 'status'

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('home')

  return (
    <div className="min-h-screen bg-background paper-texture">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-background/95 backdrop-blur border-b border-border">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-primary flex items-center justify-center text-primary-foreground font-bold">
              F
            </div>
            <div>
              <h1 className="text-lg font-bold font-display text-foreground">Form Memory</h1>
              <span className="text-xs text-muted-foreground">Thesis Formatter</span>
            </div>
          </div>

          <div className="flex gap-1">
            <button onClick={() => setCurrentPage('home')} className="nav-link px-4 py-2 text-sm">
              Home
            </button>
            <button onClick={() => setCurrentPage('generate')} className="nav-link px-4 py-2 text-sm">
              Generate
            </button>
            <button onClick={() => setCurrentPage('status')} className="nav-link px-4 py-2 text-sm">
              Status
            </button>
          </div>
        </div>
      </nav>

      {/* Content */}
      <main>
        {currentPage === 'home' && (
          <div className="space-y-20 py-12">
            {/* Hero Section */}
            <section className="max-w-7xl mx-auto px-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                <div className="space-y-8 animate-fade-in-up">
                  {/* Badge */}
                  <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full w-fit">
                    <span className="w-2 h-2 rounded-full bg-primary" />
                    <span className="text-sm font-semibold text-primary">AI-Powered</span>
                  </div>

                  {/* Headline */}
                  <h1 className="text-display leading-tight">
                    Format your thesis <span className="marker-underline">in seconds</span>
                  </h1>

                  {/* Subtitle */}
                  <p className="text-body-lg text-muted-foreground max-w-lg">
                    Works with any university template worldwide. Upload your template, content, and get a perfectly formatted thesis ready for submission.
                  </p>

                  {/* CTA Buttons */}
                  <div className="flex gap-4">
                    <Button variant="hero" onClick={() => setCurrentPage('generate')}>
                      Start Formatting
                      <ArrowRight className="ml-2 w-5 h-5" />
                    </Button>
                    <Button variant="outline">
                      See How It Works
                    </Button>
                  </div>

                  {/* Stats */}
                  <div className="flex gap-8 pt-8 border-t border-border">
                    <div>
                      <p className="text-2xl font-bold">50+</p>
                      <p className="text-sm text-muted-foreground">Universities</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold">10K+</p>
                      <p className="text-sm text-muted-foreground">Theses Formatted</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold">99%</p>
                      <p className="text-sm text-muted-foreground">Success Rate</p>
                    </div>
                  </div>
                </div>

                {/* Right side illustration */}
                <div className="relative h-96 hidden lg:block">
                  <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-accent/10 rounded-lg" />
                  <div className="absolute top-8 right-8 w-48 h-64 bg-card border border-border rounded shadow-card transform rotate-3" />
                  <div className="absolute top-16 right-24 w-48 h-64 bg-card border border-border rounded shadow-lg-card" />
                  <div className="absolute top-24 right-40 w-48 h-64 bg-card border border-border rounded shadow-card transform -rotate-3" />
                </div>
              </div>
            </section>

            {/* Features Section */}
            <section className="max-w-7xl mx-auto px-6 py-12 border-t border-border">
              <h2 className="text-subheading mb-12">Key Features</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {[
                  {
                    number: '01',
                    title: 'Template Analysis',
                    description: 'Automatically detects structure, styles, and formatting rules from any university template'
                  },
                  {
                    number: '02',
                    title: 'Content Extraction',
                    description: 'Intelligently extracts and maps your thesis content to the template structure'
                  },
                  {
                    number: '03',
                    title: 'Perfect Formatting',
                    description: 'Applies consistent formatting while preserving all styles and document integrity'
                  }
                ].map((feature, idx) => (
                  <div key={idx} className="relative animate-fade-in-up" style={{ animationDelay: `${idx * 100}ms` }}>
                    <div className="step-number">{feature.number}</div>
                    <div className="document-preview p-6 space-y-3">
                      <h3 className="font-semibold">{feature.title}</h3>
                      <p className="text-sm text-muted-foreground">{feature.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* How It Works */}
            <section className="max-w-7xl mx-auto px-6 py-12 border-t border-border">
              <h2 className="text-subheading mb-12">How It Works</h2>
              <div className="space-y-6">
                {[
                  { title: 'Upload Template', desc: 'Select your university\'s thesis template in DOCX format' },
                  { title: 'Upload Content', desc: 'Provide your thesis content as DOCX or TXT file' },
                  { title: 'Fill Details', desc: 'Enter your name, title, advisor, and other metadata' },
                  { title: 'Download', desc: 'Get your perfectly formatted thesis ready for submission' }
                ].map((step, idx) => (
                  <div key={idx} className="flex gap-6 pb-6 border-b border-border last:border-0">
                    <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <span className="font-bold text-primary">{idx + 1}</span>
                    </div>
                    <div>
                      <h3 className="font-semibold mb-1">{step.title}</h3>
                      <p className="text-sm text-muted-foreground">{step.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* CTA Banner */}
            <section className="bg-primary text-primary-foreground py-16">
              <div className="max-w-4xl mx-auto px-6 text-center space-y-6">
                <h2 className="text-subheading text-primary-foreground">Ready to format your thesis?</h2>
                <p className="text-primary-foreground/90">
                  Works with any university template. No setup required.
                </p>
                <Button variant="hero" onClick={() => setCurrentPage('generate')} className="bg-background text-primary hover:bg-card">
                  Start Now
                </Button>
              </div>
            </section>
          </div>
        )}

        {currentPage === 'generate' && <TemplateGenerator />}

        {currentPage === 'enforce' && <DocumentUploader />}

        {currentPage === 'status' && <StatusPage />}
      </main>

      {/* Footer */}
      <footer className="border-t border-border py-8 mt-20">
        <div className="max-w-7xl mx-auto px-6 text-center text-sm text-muted-foreground">
          <p>Form Memory v2.0.0 | Universal Thesis Formatter | Built with AI</p>
        </div>
      </footer>
    </div>
  )
}

export default App
