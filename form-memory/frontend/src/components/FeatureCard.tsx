import React from 'react';

interface FeatureCardProps {
  number: string;
  title: string;
  description: string;
  animationDelay?: string;
}

const FeatureCard: React.FC<FeatureCardProps> = ({ number, title, description, animationDelay }) => {
  return (
    <div className="relative animate-fade-in-up" style={{ animationDelay }}>
      <div className="step-number">{number}</div>
      <div className="document-preview p-6 space-y-3">
        <h3 className="font-semibold">{title}</h3>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
    </div>
  );
};

export { FeatureCard };