import React, { useState, useCallback } from "react";
import { Search, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { debounce } from "@/lib/utils";

interface SearchBarProps {
  placeholder?: string;
  onSearch: (query: string) => void;
  initialValue?: string;
  className?: string;
  debounceTime?: number;
  disabled?: boolean;
}

/**
 * SearchBar - Componente de barra de pesquisa com funcionalidade de debounce
 *
 * Permite a pesquisa com delay para evitar múltiplas requisições
 * enquanto o usuário ainda está digitando.
 */
const SearchBar: React.FC<SearchBarProps> = ({
  placeholder = "Buscar vagas...",
  onSearch,
  initialValue = "",
  className = "",
  debounceTime = 300,
  disabled = false,
}) => {
  const [searchQuery, setSearchQuery] = useState(initialValue);

  // Função debounce para evitar múltiplas chamadas durante digitação
  const debouncedSearch = useCallback(
    debounce((query: string) => {
      onSearch(query);
    }, debounceTime),
    [onSearch, debounceTime]
  );

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchQuery(value);
    debouncedSearch(value);
  };

  const clearSearch = () => {
    setSearchQuery("");
    onSearch("");
  };

  return (
    <div className={`relative flex items-center w-full ${className}`}>
      <div className="absolute left-3 text-gray-400">
        <Search size={18} />
      </div>
      <Input
        type="text"
        value={searchQuery}
        onChange={handleInputChange}
        placeholder={placeholder}
        className="pl-10 pr-10 w-full h-10"
        disabled={disabled}
      />
      {searchQuery && (
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className="absolute right-2"
          onClick={clearSearch}
          disabled={disabled}
        >
          <X size={16} />
          <span className="sr-only">Limpar pesquisa</span>
        </Button>
      )}
    </div>
  );
};

export default SearchBar;
