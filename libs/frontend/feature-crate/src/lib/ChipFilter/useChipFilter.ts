import type { IChipFilterProps, IUseChipFilterReturn } from './ChipFilter-types';

/** Encapsulates ChipFilter toggle logic. */
export function useChipFilter(props: IChipFilterProps): IUseChipFilterReturn {
  const { onSelectionChange, selected } = props;

  function handleToggle(value: string): void {
    const isCurrentlySelected = selected.includes(value);
    const next = isCurrentlySelected
      ? selected.filter((v) => v !== value)
      : [...selected, value];
    onSelectionChange(next);
  }

  function isSelected(value: string): boolean {
    return selected.includes(value);
  }

  return { handleToggle, isSelected };
}
