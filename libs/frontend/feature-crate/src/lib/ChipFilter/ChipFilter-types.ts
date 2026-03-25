export interface IChipFilterProps {
  /** Label for the filter group */
  label: string;
  /** Callback when selection changes */
  onSelectionChange: (selected: string[]) => void;
  /** Available options to display as chips */
  options: string[];
  /** Currently selected values */
  selected: string[];
}

export interface IUseChipFilterReturn {
  /** Handler for toggling a chip */
  handleToggle: (value: string) => void;
  /** Check if a value is selected */
  isSelected: (value: string) => boolean;
}
