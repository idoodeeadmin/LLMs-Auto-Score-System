import { Moon, Sun } from "lucide-react";
import { useTheme } from "@/contexts/ThemeContext";
import { Button } from "@/components/ui/button";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === "light" ? "dark" : "light")}
      className="rounded-full w-9 h-9 border border-slate-200 dark:border-slate-800 bg-white/50 dark:bg-slate-900/50 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
      title="Toggle Theme"
    >
      {theme === "light" ? (
        <Moon className="h-[1.1rem] w-[1.1rem] text-slate-700 dark:text-slate-300" />
      ) : (
        <Sun className="h-[1.1rem] w-[1.1rem] text-slate-300" />
      )}
      <span className="sr-only">Toggle theme</span>
    </Button>
  );
}
