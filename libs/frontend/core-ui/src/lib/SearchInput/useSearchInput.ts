import { useEffect, useRef, useState } from 'react';

import type { ISearchInputProps, IUseSearchInputReturn } from './SearchInput-types';

const DEFAULT_DEBOUNCE_MS = 300;

/** Encapsulates SearchInput debounce logic using useEffect + setTimeout. */
export function useSearchInput(props: ISearchInputProps): IUseSearchInputReturn {
  const { debounceMs = DEFAULT_DEBOUNCE_MS, onSearch, value } = props;
  const [inputValue, setInputValue] = useState(value ?? '');
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Sync controlled value from parent
  useEffect(() => {
    if (value !== undefined) {
      setInputValue(value);
    }
  }, [value]);

  // Debounce the onSearch callback
  useEffect(() => {
    timerRef.current = setTimeout(() => {
      onSearch(inputValue);
    }, debounceMs);

    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, [debounceMs, inputValue, onSearch]);

  function handleChange(event: React.ChangeEvent<HTMLInputElement>): void {
    setInputValue(event.target.value);
  }

  function handleClear(): void {
    setInputValue('');
    onSearch('');
  }

  return {
    handleChange,
    handleClear,
    inputValue,
  };
}
