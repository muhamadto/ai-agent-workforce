---
name: frontend-engineering
description: Reference knowledge for modern frontend engineering — React 18+, TypeScript 5+, Next.js 14+ App Router, Tailwind/shadcn styling, Vite/Turbopack tooling, Flutter 3.x/Dart 3+, PWAs, component and state-management patterns, web and Flutter performance, accessibility (WCAG 2.1 AA), frontend security, and the full testing stack (Vitest, RTL, Playwright, flutter_test, axe). Load this BEFORE writing, reviewing, or designing any frontend or UI code.
---

# Frontend Engineering Reference

Reference knowledge for frontend implementation work on web and cross-platform UI stacks.
Load this skill before writing, reviewing, or designing frontend code.

## React 18+ & TypeScript 5+

- **React 18+**: Server Components, Suspense, Concurrent Rendering, Transitions, useOptimistic
- **TypeScript 5+**: Strict mode, type safety, generics, utility types, const assertions, template literal types
- **React Hooks**: useState, useEffect, useContext, useMemo, useCallback, useReducer, custom hooks
- **State Management**:
  - **Zustand**: Simple global state with minimal boilerplate
  - **TanStack Query (React Query)**: Server state management, caching, mutations, optimistic updates
  - **Jotai/Recoil**: Atomic state management for complex UIs
  - **Redux Toolkit**: Only for highly complex state (last resort)
- **Component Patterns**: Compound components, render props, HOCs (sparingly), controlled/uncontrolled components

## Next.js 14+ (App Router)

- **App Router**: Server Components, Client Components, Server Actions, Route Handlers
- **Routing**: Dynamic routes, parallel routes, intercepting routes, route groups, catch-all routes
- **Data Fetching**: fetch with caching (force-cache, no-store), streaming, React Suspense
- **Special Files**: loading.tsx, error.tsx, not-found.tsx, layout.tsx, page.tsx
- **Optimization**: next/image, next/font, Script component, metadata API
- **Deployment**: Vercel, self-hosted, Docker containers, static export, edge runtime
- **Middleware**: Authentication checks, redirects, rewrites, custom headers
- **API Routes**: Route handlers (GET, POST, PUT, DELETE), webhooks, form actions

## Styling & UI

- **Tailwind CSS 3+**: Utility-first, responsive design, dark mode, custom plugins, JIT compiler
- **CSS Modules**: Scoped styling, composition, TypeScript support
- **Styled Components/Emotion**: CSS-in-JS when component-scoped styles needed
- **shadcn/ui**: Accessible component primitives built on Radix UI (copy-paste, not npm install)
- **Radix UI**: Unstyled, accessible component primitives
- **Headless UI**: Unstyled accessible components (Tailwind Labs)
- **Framer Motion**: Declarative animations, gestures, layout animations
- **Responsive Design**: Mobile-first approach, breakpoints (sm, md, lg, xl, 2xl), fluid typography

## Build Tools & Development

- **Vite**: Lightning-fast dev server, HMR, optimized builds, plugin ecosystem
- **Turbopack**: Next.js bundler (faster builds than Webpack)
- **ESLint**: Code linting with TypeScript and React rules
- **Prettier**: Opinionated code formatting
- **Husky**: Git hooks for pre-commit linting and testing
- **Biome**: Fast linter/formatter alternative to ESLint + Prettier

## Flutter 3.x & Dart 3+

- **Flutter 3.x**: Material Design 3, adaptive widgets, platform channels, Impeller rendering
- **Dart 3+**: Sound null safety, records, patterns, sealed classes, class modifiers
- **State Management**:
  - **Riverpod**: Recommended for dependency injection and state (compile-safe, testable)
  - **BLoC**: Business Logic Component pattern for complex state machines
  - **Provider**: Simpler state management (discouraged for new projects, use Riverpod)
- **Navigation**: GoRouter for declarative, type-safe routing
- **Persistence**: Hive (NoSQL), Drift (SQLite), SharedPreferences (key-value)
- **Networking**: Dio for HTTP with interceptors, Freezed for immutable models, json_serializable
- **Platform Integration**: MethodChannel, EventChannel for platform-specific code
- **Design Systems**: Material 3, Cupertino (iOS), adaptive widgets
- **Testing**: flutter_test (widget tests), integration_test (E2E), golden tests (visual regression)

## Cross-Platform & Progressive Web

- **Progressive Web Apps (PWA)**: Service workers, offline support, installability, web app manifest
- **React Native** (when needed): Expo SDK, React Native Paper, navigation
- **Responsive & Adaptive Design**: Same codebase for web, mobile, desktop

## Clean Architecture for Frontend

- **Layer Structure**:
  - **Entities (Domain)**: TypeScript interfaces, types, domain models (no framework code)
  - **Use Cases**: Business logic in custom hooks (useAuth, useCheckout, useCart)
  - **Interface Adapters**: API clients, data transformers, view models
  - **UI Layer**: Components (presentation), pages, layouts
- **Component Organization**:
  - **Presentational Components**: Receive data via props, no business logic, pure UI
  - **Container Components**: Connect to state/hooks, fetch data, pass to presentational
  - **Separation of Concerns**: Logic separate from presentation
  - **Single Source of Truth**: State managed with clear data flow (unidirectional)
- **SOLID adapted for frontend**:
  - **Single Responsibility**: Components do one thing well, custom hooks have one purpose
  - **Open/Closed**: Components extensible via props and composition, not modification
  - **Liskov Substitution**: Component variants (Button, IconButton) are interchangeable
  - **Interface Segregation**: Focused props interfaces, no kitchen-sink components
  - **Dependency Inversion**: Depend on abstractions (props interfaces, context), not implementations

## Design Patterns

- **Component Patterns**:
  - **Container/Presentational**: Separate logic from UI rendering
  - **Compound Components**: Related components that work together (Select + Option, Tabs + Tab)
  - **Render Props**: Share code between components (less common with hooks)
  - **Custom Hooks**: Reusable stateful logic (useAuth, usePagination, useDebounce)
  - **Higher-Order Components**: Component enhancement (use sparingly, prefer hooks)
  - **Provider Pattern**: Context-based dependency injection (theme, auth, i18n)
- **State Management Patterns**:
  - **Flux/Redux**: Unidirectional data flow (actions → reducers → state → UI)
  - **Observer**: Reactive state updates (subscriptions, listeners)
  - **Command**: Actions encapsulate state changes
  - **Singleton**: Global stores (Zustand, Redux)
- **Architectural Patterns**:
  - **MVVM**: Model-View-ViewModel separation
  - **Repository Pattern**: Data access abstraction (API clients)
  - **Adapter Pattern**: Transform API responses to UI models
  - **Facade Pattern**: Simplify complex API interactions
  - **Strategy Pattern**: Interchangeable rendering strategies

## Performance & Optimization

### Web Performance

- **Code Splitting**: Dynamic imports, React.lazy, Next.js automatic route-based splitting
- **Lazy Loading**: Images (next/image), components, routes
- **Memoization**: React.memo (prevent re-renders), useMemo (expensive computations), useCallback (stable function references)
- **Virtual Scrolling**: react-window, @tanstack/react-virtual for long lists (>100 items)
- **Image Optimization**: next/image, responsive images (srcset, sizes), modern formats (WebP, AVIF)
- **Caching**: HTTP caching, service workers, React Query cache
- **Bundle Optimization**: Tree shaking, minification, compression (gzip, brotli); keep bundles <200KB gzipped, monitor with webpack-bundle-analyzer
- **Critical CSS**: Inline critical styles, defer non-critical
- **Core Web Vitals targets**: LCP <2.5s, FID <100ms, CLS <0.1; Lighthouse CI in the pipeline

### Flutter Performance

- **const Constructors**: Compile-time constants for widgets (massive performance boost)
- **Widget Rebuilds**: Minimize with const, keys, ValueListenableBuilder, Riverpod selectors
- **ListView.builder**: Lazy list rendering (only renders visible items)
- **Cached Network Images**: Image caching with cached_network_image
- **Platform Views**: Optimize platform channel usage (minimize overhead)
- **Isolates**: Background computation for CPU-intensive tasks (prevent UI jank)

### User Experience

- **Loading States**: Skeletons, spinners, shimmer effects, optimistic updates
- **Error Boundaries**: Graceful error handling (React ErrorBoundary)
- **Progressive Enhancement**: Core functionality works without JS, enhanced with it
- **Offline Support**: Service workers, cache strategies (cache-first, network-first, stale-while-revalidate)
- **Responsive Images**: srcset, sizes, picture element, art direction
- **Smooth Animations**: RequestAnimationFrame, CSS transforms (not left/top), 60fps target

## Accessibility (WCAG 2.1 Level AA minimum)

- **Semantic HTML**: Proper heading hierarchy (h1-h6), landmarks (nav, main, aside), lists (ul, ol)
- **ARIA**: Roles, states, properties ONLY when semantic HTML insufficient (prefer semantic HTML)
- **Keyboard Navigation**: Focus management, tab order, keyboard shortcuts (avoid Enter/Space conflicts)
- **Screen Reader Support**: Alt text for images, aria-label/aria-labelledby, live regions (aria-live)
- **Color Contrast**: WCAG AA minimum (4.5:1 for text, 3:1 for large text/UI components)
- **Focus Indicators**: Visible focus states (outline, ring), never remove without replacement
- **Form Accessibility**: Associated labels, error messages, validation feedback, required indicators
- **Testing**: Automated (axe DevTools, axe-core, jest-axe, Lighthouse) + manual (screen reader — VoiceOver, NVDA, JAWS — and keyboard-only)

## Frontend Security

- **XSS Prevention**: Sanitize user input, avoid dangerouslySetInnerHTML (use DOMPurify if needed)
- **CSRF Protection**: Use CSRF tokens, SameSite cookies
- **Content Security Policy (CSP)**: Restrict script sources, prevent inline scripts
- **HTTPS Only**: Secure communication, HSTS headers
- **Dependency Auditing**: npm audit, Dependabot, Snyk for CVE detection
- **Secrets Management**: Never commit API keys, use environment variables (NEXT_PUBLIC_ prefix for Next.js)
- **Input Validation**: Client-side validation for UX + server-side validation for security
- **Authentication**: Secure token storage (HttpOnly cookies for web, Keychain/Keystore for mobile)

## Testing Stack

### Unit Tests (≥90% coverage)

- **React**: Vitest + React Testing Library (RTL)
  - Test component behavior, not implementation details
  - Query by accessibility attributes (role, label, text) — prefer getByRole, getByLabelText over getByTestId
  - Use userEvent for realistic interactions (@testing-library/user-event) — more realistic than fireEvent (handles focus, blur, typing delays)
  - Mock external dependencies (API calls, router, context)
  - Test user interactions and state changes from the user's perspective
  - Avoid testing internal state or private methods (test what users see)
- **Flutter**: flutter_test package
  - Widget tests for UI behavior and interactions
  - Unit tests for business logic (Riverpod providers, BLoC, utilities)
  - Mock dependencies with Mockito (HTTP clients, repositories)

### Integration Tests (≥80% coverage)

- **React**: Playwright or Cypress for E2E testing
  - Test user flows (login, checkout, form submission)
  - Test with real or near-real backend (MSW for API mocking)
  - Visual regression testing with Percy or Chromatic
  - Cross-browser testing (Chrome, Firefox, Safari, Edge)
- **Flutter**: integration_test package
  - End-to-end user flow testing across multiple screens
  - Platform-specific integration tests (iOS, Android)
  - Golden tests for visual regression (flutter test --update-goldens)

### Accessibility & Performance Tests

- **axe-core / jest-axe**: Automated accessibility testing integrated into Jest/Vitest
- **Manual**: Screen reader testing (VoiceOver, NVDA, JAWS), keyboard-only navigation
- **Lighthouse CI**: Core Web Vitals in CI pipeline
- **Bundle size monitoring**: webpack-bundle-analyzer

## Code Quality Standards

- **TypeScript Strict Mode**: Enabled, no `any` types (use `unknown` + type guards if needed)
- **Type Coverage**: Maintain >95% type coverage
- **ESLint**: Enforce code style, detect React anti-patterns, accessibility rules
- **Prettier**: Consistent code formatting
- **Bundle Size**: Monitor and optimize — code splitting, tree shaking
- **Performance**: Core Web Vitals within Google thresholds
- **Accessibility**: WCAG 2.1 Level AA compliance minimum
- No console errors or warnings in production builds; no magic strings or numbers (use constants or enums); meaningful names that reveal intent

## Related Skills

- [/api-design](../api-design/SKILL.md) — review backend API contracts before building data-fetching layers
- [/run-quality-checks](../run-quality-checks/SKILL.md) — full pre-commit quality gate (format, lint, test, SAST, SCA)
- [/dependency-review](../dependency-review/SKILL.md) — vet dependency upgrades for breaking changes, CVEs, and bundle size impact
- [/auth-engineering](../auth-engineering/SKILL.md) — secure token storage and authentication flows (delegate auth design to identity-security-developer)
- [/mobile-engineering](../mobile-engineering/SKILL.md) — native iOS/Android specifics when Flutter work crosses into platform code
