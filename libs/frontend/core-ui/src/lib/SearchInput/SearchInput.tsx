import { clearButtonStyles, inputStyles, rootStyles } from './SearchInput-elements';
import type { ISearchInputProps } from './SearchInput-types';
import { useSearchInput } from './useSearchInput';

/** Debounced search input with themed styling and inline clear button. */
export function SearchInput(props: ISearchInputProps) {
  const { placeholder = 'Search...' } = props;
  const { handleChange, handleClear, inputValue } = useSearchInput(props);

  return (
    <div className={rootStyles}>
      <input
        className={inputStyles}
        onChange={handleChange}
        placeholder={placeholder}
        type="text"
        value={inputValue}
      />
      {inputValue.length > 0 && (
        <button
          aria-label="Clear search"
          className={clearButtonStyles}
          onClick={handleClear}
          type="button"
        >
          &#x2715;
        </button>
      )}
    </div>
  );
}
