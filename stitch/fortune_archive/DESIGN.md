# Design System Strategy: The Golden Ledger

## 1. Overview & Creative North Star
**Creative North Star: "The Prestigious Archive"**
This design system moves away from the cluttered, high-anxiety aesthetics typically associated with gambling and lotteries. Instead, it adopts the persona of a high-end financial institution or a premium editorial archive. We are building a "Digital Ledger" that feels authoritative, calm, and impeccably organized.

To break the "template" look, we utilize **intentional asymmetry**—offsetting headline elements from content grids—and **tonal layering**. By favoring deep indigo depths and metallic gold accents over flat whites and generic blues, the system communicates "Trust" through "Quality."

## 2. Colors & Surface Philosophy
The palette is rooted in a "Midnight & Metallic" logic. We use deep primary blues to establish a foundation of stability, accented by secondary golds to signify "The Win" and premium value.

### The "No-Line" Rule
**Strict Mandate:** Designers are prohibited from using 1px solid borders for sectioning. 
Structure must be defined through background color shifts. A `surface-container-low` section sitting on a `surface` background creates a sophisticated boundary that feels integrated, not "boxed in." 

### Surface Hierarchy & Nesting
Treat the UI as a series of physical layers. We use the Material surface tiers to define depth without shadows:
*   **Base Layer:** `surface` (#fbf8ff) for global backgrounds.
*   **Section Layer:** `surface-container-low` (#f5f2fb) for secondary content areas.
*   **Action Layer:** `surface-container-lowest` (#ffffff) for the primary interactive cards to make them "pop" against the tinted background.

### The "Glass & Gradient" Rule
To add "soul" to the professional look, use glassmorphism for top navigation bars and floating action buttons.
*   **The Signature Gradient:** For Hero backgrounds or primary CTAs, transition from `primary` (#000666) to `primary-container` (#1a237e) at a 135-degree angle. This prevents the flat, "default" app look.

## 3. Typography
We use a dual-font strategy to balance international modernism with editorial authority.

*   **Display & Headlines (Be Vietnam Pro):** This font carries a geometric, architectural weight. Use `display-lg` to `headline-sm` for lottery names and winning numbers. The high x-height ensures clarity and a "Modern Thai" feel.
*   **Body & Labels (Plus Jakarta Sans):** Chosen for its incredible legibility at small sizes. Use this for all archival data, dates, and navigation labels.

**Hierarchy Note:** Winning numbers should always be set in `display-md` or `display-lg`, utilizing the `secondary` (Gold) color to ensure they are the first thing the eye tracks.

## 4. Elevation & Depth
We eschew traditional "Drop Shadows" in favor of **Tonal Layering** and **Ambient Light**.

*   **The Layering Principle:** Place a `surface-container-lowest` card on a `surface-container-low` background. This creates a "Natural Lift" that mimics fine stationery.
*   **Ambient Shadows:** If a card must float (e.g., a modal), use a blur of `24px` with a `4%` opacity of the `on-surface` color. It should feel like a soft glow, not a dark smudge.
*   **The "Ghost Border":** If a boundary is required for accessibility, use the `outline-variant` (#c6c5d4) at **15% opacity**. This creates a "hint" of a container without disrupting the editorial flow.

## 5. Components

### Result Cards
*   **Layout:** Forbid the use of divider lines. Separate "Draw Date" from "Winning Numbers" using a `spacing-6` (1.5rem) vertical gap.
*   **Background:** Use `surface-container-lowest`. 
*   **Regional Accents:** Use the Tertiary tokens (`tertiary`, `tertiary-fixed`) for Thai results (Green), and custom Indigo/Red overrides for Laos/Hanoi variants, but only as a subtle left-edge "accent stripe" (4px width).

### Buttons
*   **Primary:** Solid `primary` (#000666) with `on-primary` text. Use `rounded-xl` (0.75rem) for a modern, approachable feel.
*   **Secondary (The "Gold" Action):** Use `secondary-container` (#fed65b). This is reserved for "Check My Number" or "Claim" actions.

### Numbers & Digits
*   **Styling:** Winning digits should be housed in individual circular containers (`rounded-full`) using `primary-fixed` (#e0e0ff) with `on-primary-fixed` text. This makes them feel like "tokens" rather than just text.

### Navigation
*   **Bottom Bar:** Use a `surface` background with a `backdrop-blur` of 20px and 80% opacity. 
*   **Active State:** Use a `secondary-fixed` (Gold) dot indicator below the icon, rather than a thick bar.

## 6. Do’s and Don’ts

### Do:
*   **DO** use whitespace as a structural tool. If elements feel crowded, increase the spacing to `spacing-8` or `spacing-10`.
*   **DO** use the `secondary` gold sparingly. It is an "accent," not a primary background color.
*   **DO** ensure that Thai characters (Kanit/Sarabun fallbacks) have enough line-height (`1.5` minimum) to avoid clipping.

### Don’t:
*   **DON’T** use 100% black. Use `on-surface` (#1b1b21) for all "black" text to maintain the premium, softer feel.
*   **DON’T** use standard Material Design "Card Shadows." They feel too "Android 2014." Stick to tonal shifts.
*   **DON’T** use high-vibrancy "Neon" greens or reds. Use the `tertiary` and `error` tokens provided, which are calibrated for professional legibility.