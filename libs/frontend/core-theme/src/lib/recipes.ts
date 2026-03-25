/**
 * Re-export Panda CSS recipe helpers for consistent imports across libs.
 * Components import recipe utilities from core-theme rather than
 * reaching directly into the app's styled-system output.
 */

// These will be re-exported from the app's styled-system once available.
// For now, components in libs use the css() approach from their consuming app.
// This file provides a central seam for future recipe helper abstractions.

export type RecipeVariant<T> = T extends (props: infer P) => string ? P : never;
