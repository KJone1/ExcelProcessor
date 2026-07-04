# Figma Design System & Style Language Specification
## Codebase: Excel/Payslip Processor Dashboard (Apple HIG Light Edition)

This style guide acts as the single source of truth (design system) for all visual layouts, interface elements, styling tokens, and interaction behaviors developed for the custom HTML/CSS/JS dashboard application. It is modeled on high-fidelity Figma typography, color palette tokens, and standard Apple Human Interface Guidelines (HIG).

---

## 1. Vision & Core Philosophy

Our interface is designed to look like a premium, native desktop utility designed by Apple. We strictly follow these three guidelines:
*   **The Light Warm Canvas**: The application utilizes a soft, warm gray background (`#F5F5F7`) reminiscent of modern macOS settings panels.
*   **Floating Cards (Clean Layers)**: High-contrast pure white panels (`#FFFFFF`) float above the canvas. They feature generous padding, structural rounded corners, and soft, delicate drop-shadows to represent elevation.
*   **Highly Polished Interactive Controls**: Dropdowns, buttons, and text inputs are designed with solid-color blue indicators, smooth transitions, and dynamic micro-animations to reward user interaction.

---

## 2. Color Palette & UI Tokens

All colors are designed for high readability, clean contrast, and maximum aesthetic appeal. Do not use raw browser primaries (pure red, green, or blue). Instead, use these handpicked Figma color tokens:

| Token Name | Hex Code | Visual Preview / Meaning | CSS / HTML Usage |
| :--- | :--- | :--- | :--- |
| **Canvas Background** | `#F5F5F7` | Soft, warm light gray | App background |
| **Card Background** | `#FFFFFF` | Pure white sheet | Metric cards, container blocks |
| **Primary Accent** | `#0071E3` | Apple Blue | Solid buttons, active selections |
| **Primary Hover** | `#0077ED` | Lighter active blue | Button hover state |
| **System Green** | `#34C759` | Successful operations | Sync indicators, upload success |
| **System Red / Muted** | `#FF3B30` | Muted warnings / error states | Error alerts |
| **Primary Text** | `#1D1D1F` | Deep dark charcoal (near black) | Standard text, headings |
| **Secondary Text** | `#86868B` | Soft gray | Subtitles, placeholders, captions |
| **Muted Border** | `#D2D2D7` | Light gray border | Input borders, separator lines |
| **Soft Border** | `#E5E5EA` | Even lighter border | Card outlines |

---

## 3. Typography & Hierarchy

To achieve the premium look, the standard system font family should be loaded.

```css
font-family: ".AppleSystemUIFont", BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
```

### Typographic Hierarchy Tokens
*   **Application Title / Section Headers**:
    *   **Size**: `18px` to `24px`
    *   **Weight**: Bold (`font-weight: 700;`)
    *   **Color**: `#1D1D1F` (Primary Text)
*   **Body Text / Fields**:
    *   **Size**: `14px`
    *   **Weight**: Regular / Normal
    *   **Color**: `#1D1D1F`
*   **Form Labels / Captions**:
    *   **Size**: `12px`
    *   **Weight**: Medium (`font-weight: 500;`)
    *   **Color**: `#86868B` (Secondary Text)

---

## 4. Borders & Corner Radius Specs

Geometric consistency is essential to the Apple visual style.
*   **Buttons**: `border-radius: 12px;`
*   **Inputs & Uploaders**: `border-radius: 8px;`
*   **Floating Cards**: `border-radius: 12px;` with subtle drop shadow.

---

## 5. Elevation & Soft Drop-Shadows

Elevation is created using a single-layer, ultra-soft diffuse drop-shadow applied to floating card container elements:
```css
box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
```

---

## 6. CSS Integration & Directory Structure

All styling tokens and design specs are implemented in a standalone `style.css` stylesheet. The user interface references this file in the `<head>` of the HTML layout:

```html
<link rel="stylesheet" href="style.css">
```

The directory structure is organized as follows:
* `ui/index.html` - The main DOM markup for the SPA dashboard.
* `ui/style.css` - Custom style specifications.
* `ui/app.js` - Client-side interaction logic.
