import { useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  ArrowLeft, Download, FileText, Undo, Redo, Bold, Italic, Underline,
  AlignLeft, AlignCenter, AlignRight, List, ListOrdered, ZoomIn, ZoomOut,
  ChevronLeft, ChevronRight
} from 'lucide-react'

interface DocumentEditorProps {
  thesisTitle: string;
  studentName: string;
  universityName: string;
  department: string;
  advisorName: string;
  onDownload: () => void;
  onBack: () => void;
}

// Toolbar button component
const ToolbarButton = ({ children, active, onClick, className = "" }: {
  children: React.ReactNode;
  active?: boolean;
  onClick: () => void;
  className?: string;
}) => (
  <button
    onClick={onClick}
    className={`p-2 rounded hover:bg-primary/10 transition-colors ${
      active ? 'bg-primary/10 text-primary' : 'text-muted-foreground'
    } ${className}`}
  >
    {children}
  </button>
);

// Vertical divider
const ToolbarDivider = () => <div className="w-px h-6 bg-border mx-1" />;

export function DocumentEditor({
  thesisTitle,
  studentName,
  universityName,
  department,
  advisorName,
  onDownload,
  onBack,
}: DocumentEditorProps) {
  const [zoom, setZoom] = useState(100);
  const [currentPage, setCurrentPage] = useState(1);
  const [editableContent, setEditableContent] = useState({
    title: thesisTitle,
    abstract: "This thesis explores the fundamental principles and methodologies in the field of study. The research investigates key concepts, analyzes existing literature, and proposes innovative solutions to address the identified challenges. Through comprehensive analysis and empirical validation, this work contributes to the advancement of knowledge in the respective domain.",
    chapter1Title: "CHAPTER I\nINTRODUCTION",
    chapter1Content: "1.1 Background\n\nThe background of this research provides essential context for understanding the problem domain and the significance of the study.\n\n1.2 Research Problem\n\nThis section identifies and clearly defines the research problem that this thesis aims to address.\n\n1.3 Research Objectives\n\nThe primary objectives of this research are outlined to provide clear direction and purpose for the investigation."
  });

  const totalPages = 4; // Cover, Abstract, TOC, Chapter 1

  const zoomIn = () => setZoom(prev => Math.min(prev + 10, 150));
  const zoomOut = () => setZoom(prev => Math.max(prev - 10, 50));

  const goToPage = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  const updateContent = (field: keyof typeof editableContent, value: string) => {
    setEditableContent(prev => ({ ...prev, [field]: value }));
  };

  // Cover Page Component
  const CoverPage = () => (
    <div className="flex flex-col items-center justify-center min-h-full p-16 space-y-8">
      {/* University Logo Placeholder */}
      <div className="w-32 h-32 border-2 border-gray-300 flex items-center justify-center text-gray-500 font-semibold">
        LOGO
      </div>

      {/* University Name */}
      <h1 className="text-3xl font-bold tracking-widest text-center uppercase">
        {universityName}
      </h1>

      {/* Department */}
      <h2 className="text-xl font-semibold text-center">
        {department}
      </h2>

      {/* Thesis Title */}
      <div className="text-center space-y-2">
        <p className="text-lg font-medium">Thesis Title</p>
        <h3
          contentEditable
          suppressContentEditableWarning
          onInput={(e) => updateContent('title', e.currentTarget.textContent || '')}
          className="text-2xl font-bold text-center border-b-2 border-transparent hover:border-gray-300 focus:border-primary focus:outline-none px-4 py-2"
        >
          {editableContent.title}
        </h3>
      </div>

      {/* Student Info */}
      <div className="text-center space-y-4">
        <div>
          <p className="text-sm text-gray-600">Submitted by</p>
          <p className="text-lg font-medium">{studentName}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Advisor</p>
          <p className="text-lg font-medium">{advisorName}</p>
        </div>
      </div>
    </div>
  );

  // Abstract Page Component
  const AbstractPage = () => (
    <div className="p-16 space-y-8">
      <h1 className="text-3xl font-bold text-center uppercase tracking-wider">
        ABSTRACT
      </h1>

      <div
        contentEditable
        suppressContentEditableWarning
        onInput={(e) => updateContent('abstract', e.currentTarget.textContent || '')}
        className="text-justify leading-relaxed focus:outline-none focus:bg-primary/5 p-4 rounded"
        style={{ textIndent: '2em' }}
      >
        {editableContent.abstract}
      </div>
    </div>
  );

  // Table of Contents Page Component
  const TableOfContentsPage = () => (
    <div className="p-16 space-y-8">
      <h1 className="text-3xl font-bold text-center uppercase tracking-wider">
        TABLE OF CONTENTS
      </h1>

      <div className="space-y-2 font-serif">
        <div className="flex justify-between">
          <span>ABSTRACT</span>
          <span className="flex-1 border-b border-dotted border-gray-400 mx-4"></span>
          <span>ii</span>
        </div>
        <div className="flex justify-between">
          <span>LIST OF FIGURES</span>
          <span className="flex-1 border-b border-dotted border-gray-400 mx-4"></span>
          <span>iii</span>
        </div>
        <div className="flex justify-between">
          <span>LIST OF TABLES</span>
          <span className="flex-1 border-b border-dotted border-gray-400 mx-4"></span>
          <span>iv</span>
        </div>
        <div className="flex justify-between">
          <span>CHAPTER I INTRODUCTION</span>
          <span className="flex-1 border-b border-dotted border-gray-400 mx-4"></span>
          <span>1</span>
        </div>
        <div className="ml-8 flex justify-between">
          <span>1.1 Background</span>
          <span className="flex-1 border-b border-dotted border-gray-400 mx-4"></span>
          <span>1</span>
        </div>
        <div className="ml-8 flex justify-between">
          <span>1.2 Research Problem</span>
          <span className="flex-1 border-b border-dotted border-gray-400 mx-4"></span>
          <span>3</span>
        </div>
        <div className="ml-8 flex justify-between">
          <span>1.3 Research Objectives</span>
          <span className="flex-1 border-b border-dotted border-gray-400 mx-4"></span>
          <span>5</span>
        </div>
        <div className="flex justify-between">
          <span>CHAPTER II LITERATURE REVIEW</span>
          <span className="flex-1 border-b border-dotted border-gray-400 mx-4"></span>
          <span>7</span>
        </div>
        <div className="flex justify-between">
          <span>REFERENCES</span>
          <span className="flex-1 border-b border-dotted border-gray-400 mx-4"></span>
          <span>45</span>
        </div>
        <div className="flex justify-between">
          <span>APPENDIX</span>
          <span className="flex-1 border-b border-dotted border-gray-400 mx-4"></span>
          <span>52</span>
        </div>
      </div>
    </div>
  );

  // Chapter 1 Page Component
  const Chapter1Page = () => (
    <div className="p-16 space-y-8">
      <div className="text-center space-y-4">
        <h1 className="text-2xl font-bold uppercase tracking-wider">
          {editableContent.chapter1Title.split('\n')[0]}
        </h1>
        <h2 className="text-xl font-semibold">
          {editableContent.chapter1Title.split('\n')[1]}
        </h2>
      </div>

      <div
        contentEditable
        suppressContentEditableWarning
        onInput={(e) => updateContent('chapter1Content', e.currentTarget.textContent || '')}
        className="font-serif leading-relaxed focus:outline-none focus:bg-primary/5 p-4 rounded whitespace-pre-line"
        style={{ textIndent: '2em' }}
      >
        {editableContent.chapter1Content}
      </div>
    </div>
  );

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 1: return <CoverPage />;
      case 2: return <AbstractPage />;
      case 3: return <TableOfContentsPage />;
      case 4: return <Chapter1Page />;
      default: return <CoverPage />;
    }
  };

  return (
    <div className="h-screen flex flex-col bg-muted/50">
      {/* Header Toolbar */}
      <div className="bg-background border-b px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={onBack} className="flex items-center gap-2">
            <ArrowLeft className="w-4 h-4" />
            Edit Details
          </Button>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <FileText className="w-4 h-4" />
            thesis_document.docx
          </div>
        </div>
        <Button onClick={onDownload} className="flex items-center gap-2">
          <Download className="w-4 h-4" />
          Download
        </Button>
      </div>

      {/* Formatting Toolbar */}
      <div className="bg-background border-b px-4 py-2 flex items-center gap-1 flex-wrap">
        <ToolbarButton onClick={() => {}}>
          <Undo className="w-4 h-4" />
        </ToolbarButton>
        <ToolbarButton onClick={() => {}}>
          <Redo className="w-4 h-4" />
        </ToolbarButton>

        <ToolbarDivider />

        <ToolbarButton onClick={() => {}}>
          <Bold className="w-4 h-4" />
        </ToolbarButton>
        <ToolbarButton onClick={() => {}}>
          <Italic className="w-4 h-4" />
        </ToolbarButton>
        <ToolbarButton onClick={() => {}}>
          <Underline className="w-4 h-4" />
        </ToolbarButton>

        <ToolbarDivider />

        <ToolbarButton onClick={() => {}}>
          <AlignLeft className="w-4 h-4" />
        </ToolbarButton>
        <ToolbarButton onClick={() => {}}>
          <AlignCenter className="w-4 h-4" />
        </ToolbarButton>
        <ToolbarButton onClick={() => {}}>
          <AlignRight className="w-4 h-4" />
        </ToolbarButton>

        <ToolbarDivider />

        <ToolbarButton onClick={() => {}}>
          <List className="w-4 h-4" />
        </ToolbarButton>
        <ToolbarButton onClick={() => {}}>
          <ListOrdered className="w-4 h-4" />
        </ToolbarButton>

        <div className="flex-1" />

        <div className="flex items-center gap-2">
          <ToolbarButton onClick={zoomOut}>
            <ZoomOut className="w-4 h-4" />
          </ToolbarButton>
          <span className="px-3 py-1 text-sm font-medium min-w-[4rem] text-center">
            {zoom}%
          </span>
          <ToolbarButton onClick={zoomIn}>
            <ZoomIn className="w-4 h-4" />
          </ToolbarButton>
        </div>
      </div>

      {/* Document Canvas */}
      <div className="flex-1 flex items-center justify-center p-8 overflow-auto">
        <div
          className="bg-white shadow-[0_4px_30px_hsl(20_20%_12%_/_0.08)]"
          style={{
            width: `${816 * (zoom / 100)}px`,
            minHeight: `${1056 * (zoom / 100)}px`,
            transform: `scale(${zoom / 100})`,
            transformOrigin: 'top center'
          }}
        >
          <div className="w-full h-full font-serif text-black">
            {renderCurrentPage()}
          </div>
        </div>
      </div>

      {/* Page Navigation Footer */}
      <div className="bg-background border-t px-4 py-3 flex items-center justify-center gap-4">
        <button
          onClick={() => goToPage(currentPage - 1)}
          disabled={currentPage <= 1}
          className="p-2 rounded hover:bg-muted disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>

        <span className="text-sm font-medium">
          Page {currentPage} of {totalPages}
        </span>

        <button
          onClick={() => goToPage(currentPage + 1)}
          disabled={currentPage >= totalPages}
          className="p-2 rounded hover:bg-muted disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}