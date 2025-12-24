import { useState } from 'react'
import { TemplateGenerator } from '@/components/TemplateGenerator'
import { DocumentUploader } from '@/components/DocumentUploader'
import { PerfectThesisGenerator } from '@/components/PerfectThesisGenerator'
import { Button } from '@/components/ui/button'
import { ArrowRight } from 'lucide-react'
import { DocumentIllustration } from '@/components/DocumentIllustration'
import { FeatureCard } from '@/components/FeatureCard'

type Page = 'home' | 'generate' | 'perfect' | 'enforce'

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
              <button onClick={() => setCurrentPage('perfect')} className="nav-link px-4 py-2 text-sm bg-primary text-primary-foreground">
                Perfect AI
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
                 <DocumentIllustration />
              </div>
            </section>

            {/* Features Section */}
            <section className="max-w-7xl mx-auto px-6 py-12 border-t border-border">
              <h2 className="text-subheading mb-12">Key Features</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                 {[
                   {
                     number: '01',
                     title: 'AI Template Intelligence',
                     description: 'Deep analysis of any university template with automatic conversion to structured format for instant processing'
                   },
                   {
                     number: '02',
                     title: 'Content Enhancement AI',
                     description: 'Academic writing improvement, grammar correction, and quality enhancement using advanced AI models'
                   },
                   {
                     number: '03',
                     title: 'Perfect Template Matching',
                     description: 'Pixel-perfect formatting that exactly matches your university template with 100% compliance guarantee'
                   }
                 ].map((feature, idx) => (
                   <FeatureCard key={idx} number={feature.number} title={feature.title} description={feature.description} animationDelay={`${idx * 100}ms`} />
                 ))}
              </div>
            </section>

            {/* How It Works */}
            <section className="max-w-7xl mx-auto px-6 py-12 border-t border-border">
              <h2 className="text-subheading mb-12">How It Works</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
                {[
                  {
                    step: '01',
                    title: 'Upload Template',
                    desc: 'Upload your university\'s official thesis template (DOCX format)'
                  },
                  {
                    step: '02',
                    title: 'Upload Content',
                    desc: 'Add your raw thesis content (DOCX or TXT format)'
                  },
                  {
                    step: '03',
                    title: 'Perfect Formatting',
                    desc: 'AI analyzes and creates perfectly formatted thesis instantly'
                  }
                ].map((step, idx) => (
                  <div key={idx} className="text-center space-y-4">
                    <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
                      <span className="text-lg font-bold text-primary">{step.step}</span>
                    </div>
                    <h3 className="font-semibold">{step.title}</h3>
                    <p className="text-sm text-muted-foreground">{step.desc}</p>
                  </div>
                ))}
              </div>

              <div className="text-center space-y-6">
                <Button onClick={() => setCurrentPage('perfect')} className="group bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 h-12 px-8 py-4 text-lg font-semibold">
                  🚀 Perfect AI Formatting
                  <ArrowRight className="ml-2 w-5 h-5" />
                </Button>
                <div className="flex gap-3 justify-center">
                  <Button variant="outline" onClick={() => setCurrentPage('generate')}>
                    Standard Formatting
                  </Button>
                  <Button variant="ghost">
                    See How It Works
                  </Button>
                </div>
              </div>
            </section>

            {/* CTA Banner */}
            <section style={{ backgroundColor: 'rgb(37, 29, 24)' }} className="text-primary-foreground py-16">
              <div className="max-w-4xl mx-auto px-6 text-center space-y-6">
                <h2 className="text-subheading text-primary-foreground">Ready to format your thesis?</h2>
                <p className="text-primary-foreground/90">
                  Works with any university template. No setup required.
                </p>
                <Button variant="hero" onClick={() => setCurrentPage('perfect')} className="bg-background text-primary hover:bg-card">
                  Start Perfect Formatting
                </Button>
              </div>
            </section>
          </div>
        )}

        {currentPage === 'generate' && <TemplateGenerator />}

        {currentPage === 'perfect' && <PerfectThesisGenerator />}

        {currentPage === 'enforce' && <DocumentUploader />}
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
