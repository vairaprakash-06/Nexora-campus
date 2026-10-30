import React from 'react';

export const Badge = ({ children, variant = 'default', size = 'md', className = '' }) => {
  const variantStyles = {
    default: 'bg-slate-800 text-slate-300 border-slate-700',
    primary: 'bg-indigo-950/70 text-indigo-300 border-indigo-700/50',
    accent: 'bg-sky-950/70 text-sky-300 border-sky-700/50',
    success: 'bg-emerald-950/70 text-emerald-300 border-emerald-700/50',
    warning: 'bg-amber-950/70 text-amber-300 border-amber-700/50',
    danger: 'bg-rose-950/70 text-rose-300 border-rose-700/50',
    purple: 'bg-purple-950/70 text-purple-300 border-purple-700/50',
  };

  const sizeStyles = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
    lg: 'text-sm px-3 py-1.5',
  };

  return (
    <span
      className={`inline-flex items-center gap-1 font-medium rounded-full border ${variantStyles[variant] || variantStyles.default} ${sizeStyles[size]} ${className}`}
    >
      {children}
    </span>
  );
};

export default Badge;
