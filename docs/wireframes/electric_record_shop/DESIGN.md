# Design System Documentation: Digital Neon Tactility

## 1. Overview & Creative North Star

**Creative North Star: The Neon Curator**

This design system rejects the clinical, "techy" aesthetics of modern streaming apps in favor of the high-energy, tactile atmosphere of a late-night independent record shop. We are moving away from the "flat web" and into a space that feels physical, vibrant, and intentional.

To break the "template" look, we utilize **Intentional Asymmetry** and **Chromatic Depth**. Layouts should avoid perfect centering; instead, use overlapping album sleeves (cards) and high-contrast typography scales that bleed off the edges of the viewport to imply a continuous, spinning world of music. The experience should feel like flipping through a physical crate of vinyl under neon lights.

---

## 2. Colors

Our palette is rooted in a "Void Black" foundation to allow our neon accents—Electric Lime, Hot Pink, and Cyan—to vibrate with maximum intensity.

### The Palette

- **Background / Surface:** `#0e0e0e` (Deep charcoal/black foundation)
- **Primary (Electric Lime):** `primary: #f3ffca` | `primary_container: #cafd00`
- **Secondary (Hot Pink):** `secondary: #ff6b9b` | `secondary_container: #ba005b`
- **Tertiary (Cyan):** `tertiary: #a1faff` | `tertiary_container: #00f4fe`

### Color Rules

- **The "No-Line" Rule:** 1px solid borders for sectioning are strictly prohibited. Boundaries are defined solely by background shifts. For example, a `surface_container_low` section sits on a `surface` background to create a subtle "zone" without a harsh line.
- **Surface Hierarchy:** Use `surface_container` tiers (Lowest to Highest) to create a sense of "stacking."
  - _Lowest:_ Background of the app.
  - _Low/Medium:_ Sub-sections or navigation bars.
  - _High/Highest:_ Interactive cards or modal overlays.
- **The "Glass & Gradient" Rule:** For floating play-bars or sticky headers, use `surface_bright` at 60% opacity with a `20px` backdrop-blur.
- **Signature Textures:** Main Action Buttons (CTAs) should use a subtle linear gradient from `primary` to `primary_container` (135°) to give the neon a "glow" that feels liquid and premium rather than flat.

---

## 3. Typography

We utilize a high-contrast pairing: **Space Grotesk** for punchy, editorial headlines and **Manrope** for technical UI clarity.

- **Display (Space Grotesk):** `display-lg` (3.5rem). Use for "Now Playing" titles. Tighten tracking to `-0.02em`.
- **Headline (Space Grotesk):** `headline-lg` (2rem). Bold and unapologetic. Used for crate categories (e.g., "New Arrivals").
- **Body (Manrope):** `body-lg` (1rem). Used for track lists and descriptions. The clean sans-serif balances the aggressive display type.
- **Labels (Manrope):** `label-md` (0.75rem). Use for technical data (BPM, Year, Genre) in `on_surface_variant`.

---

## 4. Elevation & Depth

Depth in this system is a simulation of physical record sleeves resting on a dark workbench.

- **The Layering Principle:** Stack `surface_container_lowest` cards on `surface_container_low` backgrounds. This creates a "soft lift" that feels architectural.
- **Ambient Shadows:** For album sleeves, use a custom shadow: `0px 12px 24px rgba(0, 0, 0, 0.5)`. The shadow must be large and diffused. To mimic neon light-bleed, active cards can use a shadow tinted with `primary` at 10% opacity.
- **The "Ghost Border" Fallback:** If accessibility requires a container edge, use `outline_variant` at 15% opacity. Never use 100% opaque lines.
- **Physical Rounding:** We use a "Humanoid" rounding scale.
  - **Vinyl Sleeves:** `xl` (0.75rem) to mimic the slight wear of cardboard.
  - **Buttons:** `full` (pill-shaped) for a modern, touch-friendly feel.

---

## 5. Components

### Album Cards (The Sleeve)

- **Style:** `surface_container_highest` background.
- **Image:** 1:1 Aspect ratio.
- **Tactility:** Apply the `xl` roundedness. No borders. Use the **Ambient Shadow** rule.
- **Interaction:** On tap, the card should scale down to `0.98` to simulate a physical "press."

### Buttons

- **Primary:** Gradient of `primary` to `primary_container`. Text in `on_primary_fixed`.
- **Secondary:** Ghost style. Transparent background with a `Ghost Border` (20% opacity `secondary`). Text in `secondary`.
- **Pressed State:** Increase background brightness by 10% and remove the shadow to imply the button has been physically pushed into the surface.

### The Queue List

- **Constraint:** **Forbid divider lines.**
- **Separation:** Use `spacing: 2` (0.7rem) between items. Distinguish the "Current Track" by giving it a `surface_container_high` background while the "Next Up" items remain on the base `surface`.

### Interactive Chips

- **Filter Chips:** Use `surface_variant` for unselected states. On selection, switch to `secondary_container` with `on_secondary_container` text. This provides a "pop" of neon color in a dark UI.

### The Playback Progress Bar

- **Style:** A thick, `4px` track.
- **Track:** `surface_variant`.
- **Indicator:** `tertiary` (Cyan) with a `4px` outer glow (drop shadow) using the same color.

---

## 6. Do's and Don'ts

### Do

- **Do** use overlapping elements. Let an album sleeve partially cover a header to create depth.
- **Do** use Electric Lime (`primary`) for success or positive actions and Hot Pink (`secondary`) for energy or attention-grabbing.
- **Do** treat white space as "negative pressure." Large gaps (using `spacing: 12` or `16`) make the neon elements feel more precious.

### Don't

- **Don't** use pure blue or "tech" gradients. If it looks like a bank app, it's wrong.
- **Don't** use 1px dividers. It breaks the "Record Shop" vibe and makes the UI feel like a spreadsheet.
- **Don't** use vintage textures (paper grains, leather). The "Neon" feel comes from color and light, not literal skeuomorphism.
- **Don't** use "Cream" or "Off-white" for text. Use pure `#ffffff` or the tinted `primary_dim` for a crisp, digital-first look.
