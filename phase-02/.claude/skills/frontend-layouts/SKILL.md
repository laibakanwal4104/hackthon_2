---
name: frontend-layouts
description: Build modern frontend pages, reusable components, and styled layouts. Use for web app or website development.
---

# Frontend Skill: Pages, Components, Layouts, Styling

## Instructions

1. **Page Structure**
   - Use semantic HTML elements (`<header>`, `<main>`, `<footer>`)
   - Divide content into sections for readability
   - Use container and grid systems for layout consistency

2. **Components**
   - Create reusable UI components (buttons, cards, forms)
   - Keep components self-contained with minimal dependencies
   - Pass dynamic data via props (for frameworks like React/Vue)

3. **Layouts**
   - Implement responsive grids (Flexbox, CSS Grid)
   - Create modular sections that adapt to different screen sizes
   - Use spacing utilities (margins, padding) consistently

4. **Styling**
   - Use CSS variables for theme colors and fonts
   - Implement hover and focus states for interactive elements
   - Maintain consistent typography and color hierarchy

5. **Best Practices**
   - Mobile-first design
   - Keep CSS modular and avoid global overrides
   - Comment complex layout or styling logic
   - Optimize images and assets for performance

## Example Component Structure

```html
<section class="section-container">
  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
    <div class="card">
      <h2 class="card-title">Component Title</h2>
      <p class="card-text">Some descriptive text for this component.</p>
      <button class="btn-primary">Action</button>
    </div>
    <div class="card">
      <h2 class="card-title">Another Component</h2>
      <p class="card-text">Supporting content goes here.</p>
      <button class="btn-secondary">Learn More</button>
    </div>
  </div>
</section>
