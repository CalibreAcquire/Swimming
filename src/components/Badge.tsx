const PALETTES: Record<string, string> = {
  slate: "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300",
  green: "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-400",
  amber: "bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-400",
  red: "bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-400",
  blue: "bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-400",
};

export function Badge({ children, color = "slate" }: { children: React.ReactNode; color?: keyof typeof PALETTES }) {
  return <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${PALETTES[color]}`}>{children}</span>;
}
