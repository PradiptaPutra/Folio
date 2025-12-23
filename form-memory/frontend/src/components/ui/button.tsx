import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cn } from "@/lib/utils"

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  asChild?: boolean
  variant?: 'default' | 'hero' | 'outline' | 'minimal' | 'ghost'
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, asChild = false, variant = 'default', ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    
    const baseStyles = "inline-flex items-center justify-center whitespace-nowrap transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
    
    const variants = {
      default: "h-10 px-4 py-2 bg-primary text-primary-foreground rounded shadow-card hover:shadow-lg-card hover:-translate-y-0.5",
      hero: "h-12 px-8 py-4 bg-primary text-primary-foreground rounded text-lg font-semibold shadow-lg-card hover:shadow-2xl hover:-translate-y-1",
      outline: "h-10 px-4 py-2 border-2 border-primary text-primary rounded hover:bg-primary hover:text-primary-foreground",
      minimal: "h-10 px-4 py-2 text-foreground hover:text-primary relative",
      ghost: "h-10 px-4 py-2 text-foreground hover:bg-muted rounded"
    }
    
    return (
      <Comp
        className={cn(baseStyles, variants[variant], className)}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button }
