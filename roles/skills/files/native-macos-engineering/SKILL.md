---
name: native-macos-engineering
description: Reference knowledge for native macOS application engineering — Swift 6 language features, SwiftUI for macOS, AppKit, App Sandbox entitlements, security-scoped bookmarks, and Mac App Store notarisation/distribution. Load this BEFORE writing, reviewing, or designing any native macOS code.
---

# Native macOS Engineering

Full-stack reference for building native macOS applications — window/menu-bar-based utilities, full document-based apps, and everything App Sandbox touches. Distinct from `mobile-engineering`: iOS/iPadOS/watchOS/tvOS and cross-platform mobile targets stay with **mobile-engineer**, even where the SwiftUI code looks identical to macOS SwiftUI. This skill owns macOS-desktop-specific APIs, sandboxing, and distribution.

## Swift 6 Language Features

- **Strict concurrency by default**: every type crossing an isolation boundary must be `Sendable` (or explicitly `@unchecked Sendable` with a documented reason — never as a default escape hatch). Prefer `actor` for genuinely concurrent mutable state; prefer `@MainActor` isolation for anything driven by user interaction (menu clicks, button handlers) rather than manual locking.
- **Two-lifetime dependency injection**: construction-time injection for stable dependencies (resolved bookmarks, configuration); per-call parameters for values that change every invocation (resolved date intervals, live state) — avoids caching staleness and keeps types testable with fixture data.
- **Typed throws** and closed `Error` enums: prefer classified, non-string-carrying error cases (e.g. an OS return code as `Int32`, or a closed reason enum) over interpolating an underlying `Error`'s description — a `CocoaError`'s own description commonly contains the file path, which is exactly the kind of content a security-conscious app must not let leak into logs.
- **Macros**: `@State`/`@Binding`/`@Observable` etc. rely on the `SwiftUIMacros`/`ObservationMacros` compiler plugins bundled with full Xcode.app — these are **not** available under Xcode Command Line Tools alone. A pure-logic Swift package (no `import SwiftUI`) still builds and tests fine under Command Line Tools; anything importing SwiftUI needs full Xcode installed to compile.

## SwiftUI for macOS

- **Window/scene management**: `WindowGroup`, `Window`, `Settings` scene (for a dedicated Settings window), `MenuBarExtra` (SwiftUI's built-in menu-bar scene — evaluate against `NSStatusItem`+`NSPopover` per-project: `MenuBarExtra` has historically had gaps in system-panel access, keyboard-focus reliability inside its content, and icon-redraw correctness across macOS versions; re-verify against the current macOS/Xcode release rather than assuming either is uniformly better).
- **Menu bar commands**: the `Commands` scene modifier for a document-based app's menu bar (File/Edit/View menus), distinct from a menu-bar-*utility* app (an icon living in the system status bar, not a Dock app with its own menu bar).
- Popover-hosted content should avoid nested `clipShape` calls that double up on a container's own corner radius (visible seam artefacts); pin chrome (headers, footers, status areas) outside any internal `ScrollView` so only the scrollable content region moves.
- `.preferredColorScheme(...)` inside a SwiftUI view is a *content-only* approximation of real AppKit vibrancy (`NSVisualEffectView`) — swapping a `.preferredColorScheme(.dark)` flat-fill approximation for a real `NSVisualEffectView(material:blendingMode:state:)` container, once a real app target exists, is a container-level change, not a content rewrite, as long as the SwiftUI view's own colours are fixed tokens rather than derived from `@Environment(\.colorScheme)`.

## AppKit

- **`NSStatusItem`**: one instance per menu-bar icon. For an app showing multiple simultaneous indicators (e.g. one badge per data source), prefer one `NSStatusItem` per indicator over a single custom view with manual layout — this gets free click hit-testing and free per-item right-click menu wiring, at the cost of managing an array of status items that must be constructed/torn down as the underlying data changes (e.g. as a user enables/disables sources in Settings).
- **`NSPopover`**: the standard container for menu-bar-utility content. Attach via `NSPopover.show(relativeTo:of:preferredEdge:)` against the status item's button; dismiss on outside click (`.transient` behavior) or pin open (`.applicationDefined`) depending on whether the content needs sustained interaction (a Settings panel) vs. a glanceable summary.
- **`NSWindow`/`NSViewController`**: for any full window (a Settings window, an about panel) hosted from a `LSUIElement` (menu-bar-only, no Dock icon) app. `LSUIElement = true` in `Info.plist` is what makes an app menu-bar-only; the app must still explicitly activate itself (`NSApplication.shared.activate()`, replacing the pre-macOS-14-deprecated `NSApp.activate(ignoringOtherApps:)`) before presenting any modal panel (`NSOpenPanel.runModal()`, an alert) — a backgrounded/accessory app's activation request can otherwise be silently throttled by the OS, so call `activate()` synchronously, in the same call stack as the triggering event, with no `await`/suspension point in between.
- **`NSOpenPanel`**: runs out-of-process via `com.apple.appkit.xpc.openAndSavePanelService` under App Sandbox — this means it cannot be driven by automated UI tests; design the calling code so the panel-presenting call sits behind a narrow protocol seam, letting everything else (the decision logic before/after the panel) stay unit-testable while the panel itself is exercised via a manual per-release checklist.

## App Sandbox & Entitlements

- **Full sandbox** (`com.apple.security.app-sandbox`): mandatory for Mac App Store distribution, strongly recommended even for direct-distribution apps as a defense-in-depth boundary. Keep the entitlement list minimal and exact — CI should assert exact key→value pairs (e.g. `app-sandbox == true`, not just that the key is present), since a misconfigured `false` value would otherwise pass a presence-only check.
- **`com.apple.security.files.user-selected.read-only`**: grants read-only access to a user-selected file/folder via the Powerbox (`NSOpenPanel`) flow — required for any sandboxed app that reads outside its own container without a broader (and harder to justify) entitlement.
- **No entitlement without a corresponding user-facing grant flow.** Every entitlement should map to an explicit, auditable reason a reviewer (Mac App Store or otherwise) can verify against the app's actual behaviour.

## Security-Scoped Bookmarks

- **Persisting sandboxed file access across launches**: `url.bookmarkData(options: [.withSecurityScope, .securityScopeAllowOnlyReadAccess], ...)` at grant time; store the resulting `Data` (0600 permissions, created atomically with the correct mode from the first syscall — write-then-chmod leaves a brief window at default permissions for genuinely sensitive data). Resolve with `URL(resolvingBookmarkData:options: [.withSecurityScope], relativeTo:, bookmarkDataIsStale:)` on each subsequent launch.
- **Stale-flag handling**: a `true` `bookmarkDataIsStale` on resolution means the bookmark still resolves but should be re-issued from the resolved URL before the next persist — never a hard failure on its own.
- **Balanced access**: every `startAccessingSecurityScopedResource()` must be matched with `stopAccessingSecurityScopedResource()`, ideally via a `defer` immediately after a successful start so every exit path (including a thrown error) balances correctly. **Always check the `Bool` return of `startAccessingSecurityScopedResource()`** — a `false` return means access wasn't actually granted, and proceeding to read the URL anyway is silently accessing something the app doesn't actually have a live extent for; route a `false` return into the same degraded/error-handling path as any other access failure.
- **Identity-bound**: a security-scoped bookmark is tied to the app's code-signing identity (or Team ID) — bookmarks created under one identity are inert if copied to a different machine/account, or after a signing-identity change (ad-hoc signing churns identity across rebuilds, so expect re-grant prompts during local development that a Developer ID-signed release build won't have).

## Mac App Store Notarisation & Distribution

- **Ad-hoc signing** (no Developer ID) embeds sandbox entitlements fine for local/personal use, but every rebuild's identity churn means bookmarks and system registrations (e.g. `SMAppService` launch-at-login) may need re-granting.
- **Notarisation** requires a paid Apple Developer Program membership and a Developer ID signing identity — it's a Gatekeeper trust mechanism, orthogonal to sandboxing (a fully sandboxed app can still be un-notarised, and vice versa).
- **Distributing an un-notarised, ad-hoc-signed build outside the Mac App Store** (e.g. a direct GitHub Release download) triggers Gatekeeper's quarantine flag on every fresh download — `xattr -dr com.apple.quarantine <path>` or the GUI "Open Anyway" flow (System Settings → Privacy & Security) is the recurring (not one-time) workaround. A public release download page should verify a published checksum (SHA256) **before** running any quarantine bypass — the bypass step is otherwise indistinguishable from what a tampered or spoofed lookalike release would also instruct a victim to do.
- **Mac App Store distribution** requires the full sandbox entitlement, notarisation via the standard App Store review pipeline (not manual `notarytool` submission), and compliance with App Store Review Guidelines (no private API usage, accurate entitlement justification).
