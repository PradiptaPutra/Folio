import React from 'react';

const DocumentIllustration: React.FC = () => {
  return (
    <div className="relative h-96 hidden lg:block">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-accent/10 rounded-lg" />
      <div className="absolute top-8 right-8 w-48 h-64 bg-card border border-border rounded shadow-card transform rotate-3" />
      <div className="absolute top-16 right-24 w-48 h-64 bg-card border border-border rounded shadow-lg-card" />
      <div className="absolute top-24 right-40 w-48 h-64 bg-card border border-border rounded shadow-card transform -rotate-3" />
    </div>
  );
};

export { DocumentIllustration };