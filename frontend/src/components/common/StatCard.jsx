import React from 'react';

export const StatCard = ({ title, value, subtitle, icon: Icon, trend, variant = 'default' }) => {
  const borderStyles = {
    default: 'hover:border-slate-700',
    blue: 'hover:border-sky-500/50',
    indigo: 'hover:border-indigo-500/50',
    emerald: 'hover:border-emerald-500/50',
    amber: 'hover:border-amber-500/50',
    rose: 'hover:border-rose-500/50',
  };

  const iconBgStyles = {
    default: 'bg-slate-800/80 text-slate-300',
    blue: 'bg-sky-950/80 text-sky-400 border border-sky-800/50',
    indigo: 'bg-indigo-950/80 text-indigo-400 border border-indigo-800/50',
    emerald: 'bg-emerald-950/80 text-emerald-400 border border-emerald-800/50',
    amber: 'bg-amber-950/80 text-amber-400 border border-amber-800/50',
    rose: 'bg-rose-950/80 text-rose-400 border border-rose-800/50',
  };

  return (
    <div className={`bg-campus-card/90 border border-campus-border rounded-xl p-5 transition-all-200 ${borderStyles[variant]} shadow-lg hover:shadow-xl`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-campus-muted">{title}</p>
          <h3 className="text-2xl font-bold text-white mt-1 font-mono">{value}</h3>
          {subtitle && (
            <p className="text-xs text-slate-400 mt-1 flex items-center gap-1">
              {subtitle}
            </p>
          )}
        </div>
        {Icon && (
          <div className={`p-3 rounded-lg ${iconBgStyles[variant]}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
      {trend && (
        <div className="mt-3 pt-3 border-t border-slate-800/60 flex items-center text-xs">
          <span className={trend.isPositive ? 'text-emerald-400' : 'text-rose-400'}>
            {trend.value}
          </span>
          <span className="text-slate-500 ml-1.5">{trend.label}</span>
        </div>
      )}
    </div>
  );
};

export default StatCard;
