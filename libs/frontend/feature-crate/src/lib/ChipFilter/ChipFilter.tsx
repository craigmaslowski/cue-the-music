import {
  chipRowStyles,
  chipSelectedStyles,
  chipStyles,
  labelStyles,
  rootStyles,
} from './ChipFilter-elements';
import type { IChipFilterProps } from './ChipFilter-types';
import { useChipFilter } from './useChipFilter';

/** Multi-select filter chip group for genre or decade filtering. */
export function ChipFilter(props: IChipFilterProps) {
  const { label, options } = props;
  const { handleToggle, isSelected } = useChipFilter(props);

  return (
    <div className={rootStyles}>
      <span className={labelStyles}>{label}</span>
      <div className={chipRowStyles}>
        {options.map((option) => (
          <button
            className={isSelected(option) ? chipSelectedStyles : chipStyles}
            key={option}
            onClick={() => handleToggle(option)}
            type="button"
          >
            {option}
          </button>
        ))}
      </div>
    </div>
  );
}
