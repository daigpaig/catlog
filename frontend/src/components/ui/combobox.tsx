import * as React from "react";
import { Check, ChevronsUpDown, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { Input } from "@/components/ui/input";

interface ComboboxProps {
  options: string[];
  values: string[];
  onChange: (values: string[]) => void;
  placeholder?: string;
  searchPlaceholder?: string;
  emptyText?: string;
  className?: string;
}

export function Combobox({
  options,
  values,
  onChange,
  placeholder = "Select items...",
  searchPlaceholder = "Search...",
  emptyText = "No items found.",
  className,
}: ComboboxProps) {
  const [open, setOpen] = React.useState(false);
  const [search, setSearch] = React.useState("");
  const comboboxRef = React.useRef<HTMLDivElement>(null);

  const filteredOptions = React.useMemo(() => {
    if (!search) return options;
    const lowerSearch = search.toLowerCase();
    return options.filter((option) =>
      option.toLowerCase().includes(lowerSearch)
    );
  }, [options, search]);

  const handleToggle = (option: string) => {
    const newValues = values.includes(option)
      ? values.filter((v) => v !== option)
      : [...values, option];
    onChange(newValues);
  };

  const handleRemove = (option: string, e: React.MouseEvent) => {
    e.stopPropagation();
    onChange(values.filter((v) => v !== option));
  };

  // Close dropdown when clicking outside
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (comboboxRef.current && !comboboxRef.current.contains(event.target as Node)) {
        setOpen(false);
        setSearch("");
      }
    };

    if (open) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [open]);

  return (
    <div ref={comboboxRef} className={cn("relative w-full", className)}>
      <button
        type="button"
        role="combobox"
        aria-expanded={open}
        onClick={() => setOpen(!open)}
        className={cn(
          "w-full flex items-center justify-between gap-2 rounded-md border border-gray-600 bg-gray-900 px-3 py-2.5 text-sm text-white hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all min-h-[2.5rem]",
          open && "ring-2 ring-blue-500/50 border-blue-500 bg-gray-800"
        )}
      >
        <div className="flex flex-wrap gap-1.5 flex-1 min-w-0 text-left">
          {values.length === 0 ? (
            <span className="text-gray-400 text-sm">{placeholder}</span>
          ) : (
            values.map((value) => (
              <span
                key={value}
                className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-gray-700/80 text-xs font-medium text-white border border-gray-600/50 hover:bg-gray-700 transition-colors group"
                onClick={(e) => {
                  e.stopPropagation();
                  handleRemove(value, e);
                }}
              >
                <span className="max-w-[200px] truncate">{value}</span>
                <X className="h-3 w-3 cursor-pointer hover:text-red-400 transition-colors opacity-70 group-hover:opacity-100 flex-shrink-0" />
              </span>
            ))
          )}
        </div>
        <ChevronsUpDown className={cn(
          "h-4 w-4 shrink-0 transition-transform duration-200",
          open ? "opacity-100 rotate-180" : "opacity-60"
        )} />
      </button>
      
      {open && (
        <div className="absolute z-50 w-full mt-1.5 bg-gray-800 border border-gray-600 rounded-lg shadow-xl overflow-hidden">
          <div className="p-2.5 border-b border-gray-700/50">
            <Input
              placeholder={searchPlaceholder}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="bg-gray-900 border-gray-600 text-white placeholder:text-gray-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500/50"
              onClick={(e) => e.stopPropagation()}
              autoFocus
            />
          </div>
          <div className="max-h-[240px] overflow-auto [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar-track]:bg-gray-800 [&::-webkit-scrollbar-thumb]:bg-gray-600 [&::-webkit-scrollbar-thumb]:rounded-full">
            {filteredOptions.length === 0 ? (
              <div className="p-4 text-center text-sm text-gray-400">
                {emptyText}
              </div>
            ) : (
              filteredOptions.map((option) => {
                const isSelected = values.includes(option);
                return (
                  <div
                    key={option}
                    className={cn(
                      "relative flex cursor-pointer select-none items-center px-3 py-2.5 text-sm outline-none text-white transition-colors",
                      isSelected 
                        ? "bg-blue-600/20 hover:bg-blue-600/30" 
                        : "hover:bg-gray-700/50"
                    )}
                    onClick={() => handleToggle(option)}
                  >
                    <div className={cn(
                      "flex items-center justify-center w-4 h-4 rounded border-2 mr-3 transition-all flex-shrink-0",
                      isSelected 
                        ? "bg-blue-600 border-blue-600" 
                        : "border-gray-500 bg-transparent"
                    )}>
                      <Check
                        className={cn(
                          "h-3 w-3 text-white transition-opacity",
                          isSelected ? "opacity-100" : "opacity-0"
                        )}
                      />
                    </div>
                    <span className="flex-1">{option}</span>
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
}
