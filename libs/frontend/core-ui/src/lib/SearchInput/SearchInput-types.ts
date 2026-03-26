export interface ISearchInputProps {
  /** Debounce delay in milliseconds (defaults to 300) */
  debounceMs?: number;
  /** Callback fired with the debounced search value */
  onSearch: (value: string) => void;
  /** Placeholder text shown when the input is empty */
  placeholder?: string;
  /** Current search value (controlled mode) */
  value?: string;
}

export interface IUseSearchInputReturn {
  /** Handler for input change events */
  handleChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  /** Handler for clearing the input */
  handleClear: () => void;
  /** Current input display value (may differ from debounced value) */
  inputValue: string;
}
