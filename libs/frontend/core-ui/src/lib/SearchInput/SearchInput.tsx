import { inputStyles, rootStyles } from './SearchInput-elements';
import type { ISearchInputProps } from './SearchInput-types';
import { useSearchInput } from './useSearchInput';

/** Debounced search input with themed styling. */
export function SearchInput(props: ISearchInputProps) {
  const { placeholder = 'Search...' } = props;
  const { handleChange, inputValue } = useSearchInput(props);

  return (
    <div className={rootStyles}>
      <input
        className={inputStyles}
        onChange={handleChange}
        placeholder={placeholder}
        type="text"
        value={inputValue}
      />
    </div>
  );
}
