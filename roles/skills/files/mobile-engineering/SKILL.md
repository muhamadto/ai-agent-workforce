---
name: mobile-engineering
description: Reference knowledge for mobile engineering — iOS (Swift 6+, SwiftUI, UIKit, Combine, iOS frameworks), Android (Kotlin 2+, Jetpack Compose, Jetpack libraries), Flutter 3.x/Dart 3+, React Native, platform-specific features (biometrics, Keychain/Keystore, push notifications, deep linking, location, camera, offline-first), app store distribution, mobile CI/CD (Fastlane), performance tuning, mobile testing stacks, and mobile accessibility. Load this BEFORE writing, reviewing, or designing any mobile code.
---

# Mobile Engineering Reference

Reference knowledge for native iOS, Android, and cross-platform mobile implementation work.
Load this skill before writing, reviewing, or designing mobile code.

## iOS Development

### Swift & SwiftUI

- **Swift 6+**: Modern, type-safe language, value semantics, protocol-oriented programming
- **SwiftUI**: Declarative UI framework, state management, Combine integration
- **UIKit**: Imperative UI (when SwiftUI insufficient), view controllers, auto layout
- **Combine**: Reactive programming, publishers, subscribers, operators
- **Concurrency**: async/await, actors, structured concurrency, tasks, task groups
- **Swift Package Manager (SPM)**: Dependency management, modular libraries

### iOS Frameworks

- **Foundation**: Core data types, networking (URLSession), file management
- **Core Data**: Local persistence, object graph management, migration
- **CloudKit**: iCloud integration, sync, notifications
- **Core Location**: GPS, geofencing, location updates
- **Core Motion**: Accelerometer, gyroscope, motion tracking
- **ARKit**: Augmented reality, world tracking, face tracking
- **HealthKit**: Health data integration
- **StoreKit**: In-app purchases, subscriptions
- **Push Notifications**: APNs (Apple Push Notification service), remote and local notifications
- **Universal Links**: Deep linking, app-web integration
- **Widgets**: Home screen widgets, lock screen widgets

### iOS Architecture Patterns

- **MVVM (Model-View-ViewModel)**: Separation of concerns, binding, testability
- **MVI (Model-View-Intent)**: Unidirectional data flow, state management
- **Clean Architecture**: Domain layer, use cases, repositories (adapted for iOS)
- **Coordinator Pattern**: Navigation management, decoupled view controllers
- **Repository Pattern**: Data access abstraction (network + local)

## Android Development

### Kotlin & Jetpack Compose

- **Kotlin 2.0+**: Null safety, coroutines, extension functions, sealed classes, data classes
- **Jetpack Compose**: Declarative UI, state management, recomposition, side effects
- **Android Views (XML)**: Legacy UI (when Compose insufficient), layouts, view binding
- **Kotlin Coroutines**: Async programming, suspend functions, flows, channels
- **Kotlin Flow**: Reactive streams, cold streams, state flow, shared flow

### Android Jetpack Libraries

- **Compose**: UI toolkit (compose-ui, compose-material3, compose-navigation)
- **Navigation**: Navigation component, safe args, deep links
- **Room**: Local database (SQLite wrapper), DAOs, entities, migrations
- **ViewModel**: Lifecycle-aware state holder, survive configuration changes
- **LiveData / StateFlow**: Observable data holders, lifecycle-aware
- **WorkManager**: Background tasks, constraints, periodic work
- **Paging**: Paginated data loading, incremental loading
- **Hilt / Koin**: Dependency injection (Hilt official, Koin lightweight)
- **DataStore**: Key-value and proto storage (SharedPreferences replacement)
- **CameraX**: Camera API, image capture, video capture, analysis

### Android Architecture Patterns

- **MVVM (Model-View-ViewModel)**: Recommended by Google, ViewModel + LiveData/Flow
- **MVI (Model-View-Intent)**: Unidirectional data flow, immutable state
- **Clean Architecture**: Domain, data, presentation layers
- **Repository Pattern**: Single source of truth, network + cache

## Cross-Platform Development

### Flutter & Dart

- **Flutter 3.x**: Cross-platform (iOS, Android, Web, Desktop), single codebase
- **Dart 3+**: Sound null safety, async/await, streams, isolates
- **Widgets**: Stateless, stateful, inherited widgets
- **State Management**: Riverpod (recommended), BLoC, Provider, GetX
- **Navigation**: GoRouter for type-safe navigation
- **Platform Channels**: MethodChannel, EventChannel for native code integration
- **Plugins**: Access platform-specific features (camera, location, sensors)
- **Material Design 3**: Modern UI components
- **Cupertino**: iOS-style widgets
- **Package Manager**: pub.dev for packages

### React Native & TypeScript

- **React Native**: JavaScript bridge to native, hot reload, large ecosystem
- **TypeScript**: Type safety, better tooling
- **React Hooks**: useState, useEffect, useContext, custom hooks
- **Navigation**: React Navigation for stack, tab, drawer navigation
- **State Management**: Redux Toolkit, Zustand, Jotai, Context API
- **Native Modules**: Bridge to native code (Swift, Kotlin)
- **Expo**: Managed workflow, OTA updates, easier setup
- **Libraries**: React Native Paper (Material), NativeBase, Tamagui

## Platform-Specific Features

### Authentication & Security

- **Biometric Authentication**:
  - iOS: Face ID, Touch ID (LocalAuthentication framework)
  - Android: BiometricPrompt API (fingerprint, face unlock)
- **Keychain / Keystore**:
  - iOS: Keychain Services for secure storage
  - Android: Keystore system for cryptographic keys
- **SSL Pinning**: Certificate pinning to prevent MITM attacks
- **Code Obfuscation**: ProGuard (Android), code obfuscation (iOS)
- **Jailbreak / Root Detection**: Detect compromised devices (financial or high-security apps)
- **Secure Storage**: Never UserDefaults/SharedPreferences for secrets
- **Network Security**: HTTPS only; SSL pinning for high-security apps
- **Input Validation**: Sanitize user input, prevent injection; minimize sensitive logic in the client

### Push Notifications

- **iOS**: APNs (Apple Push Notification service), device tokens, silent notifications
- **Android**: FCM (Firebase Cloud Messaging), notification channels, foreground services
- **Cross-Platform**: OneSignal, Firebase Cloud Messaging (both platforms)

### Deep Linking & Universal Links

- **iOS**: Universal Links (web → app), URL Schemes (app → app)
- **Android**: App Links (web → app), intent filters
- **Branch / Firebase Dynamic Links**: Advanced deep linking, deferred deep linking

### Location & Maps

- **iOS**: Core Location, MapKit, significant location changes
- **Android**: Fused Location Provider, Google Maps SDK
- **Cross-Platform**: Google Maps Flutter, Mapbox

### Camera & Media

- **iOS**: AVFoundation (camera), PhotoKit (photo library)
- **Android**: CameraX (recommended), MediaStore (gallery)
- **Cross-Platform**: image_picker, camera plugins

### Offline-First Architecture

- **Local Persistence**:
  - iOS: Core Data, SQLite, Realm
  - Android: Room, SQLite, Realm
  - Flutter: Hive, Drift, Isar
- **Sync Strategy**: Conflict resolution, last-write-wins, CRDTs
- **Network Availability**: Reachability (iOS), ConnectivityManager (Android)
- **Queue Network Requests**: Retry on reconnection

## App Distribution & CI/CD

### iOS App Store

- **Xcode Cloud / App Store Connect**: Submit builds, TestFlight, app review
- **TestFlight**: Beta testing, internal and external testers
- **App Store Guidelines**: Review guidelines, rejection reasons, appeals
- **Provisioning**: Development, ad-hoc, distribution certificates and profiles
- **App Signing**: Code signing, automatic vs manual signing

### Android Play Store

- **Google Play Console**: Upload APK/AAB, internal/closed/open testing
- **App Bundles (AAB)**: Optimized delivery, smaller downloads
- **Play Store Guidelines**: Content policy, review process
- **Signing**: Upload key, app signing by Google Play

### CI/CD for Mobile

- **Fastlane**: Automate screenshots, beta deployments, app store submissions
  - Match: Code signing management
  - Gym: Build iOS apps
  - Pilot: TestFlight deployment
  - Supply: Play Store deployment
- **GitHub Actions**: CI/CD workflows, build and test automation
- **Bitrise**: Mobile-focused CI/CD platform
- **Codemagic**: Flutter and React Native CI/CD
- **Firebase App Distribution**: Beta testing alternative to TestFlight/Play Console

## Performance Optimization

### iOS Performance

- **Startup Time**: Optimize app launch, lazy loading, defer initialization
- **Memory Management**: ARC (Automatic Reference Counting), avoid retain cycles, weak/unowned references
- **Battery Efficiency**: Minimize location updates, batch network requests, background task optimization
- **Instruments**: Profiling (time profiler, allocations, leaks, energy log)
- **Metal**: GPU acceleration for graphics-intensive apps

### Android Performance

- **Startup Time**: Lazy initialization, content providers optimization
- **Memory Management**: Lifecycle-aware components, avoid memory leaks (viewModel, context leaks)
- **Battery Efficiency**: Doze mode, app standby, JobScheduler, WorkManager
- **Profiling**: Android Profiler (CPU, memory, network, energy)
- **Jetpack Compose Performance**: Recomposition optimization, remember, derivedStateOf

### Cross-Platform Performance

- **Flutter**: Skia rendering, Impeller (new renderer), const constructors, ListView.builder
- **React Native**: Hermes engine, FlatList optimization, useMemo, useCallback
- **Network Optimization**: Image caching, HTTP/2, compression, pagination

## Testing Stacks

### iOS Testing

- **XCTest**: Unit tests, UI tests (XCUITest)
- **Quick / Nimble**: BDD-style testing (more expressive)
- **Mocking**: Protocols for dependency injection, mock objects
- **Snapshot Testing**: UI regression testing (iOSSnapshotTestCase)

### Android Testing

- **JUnit 5**: Unit tests
- **Espresso**: UI testing (interact with views, assertions)
- **Mockk / Mockito**: Mocking framework
- **Robolectric**: Unit tests with Android framework (faster than emulator)
- **Screenshot Testing**: Paparazzi, Shot for UI regression

### Cross-Platform Testing

- **Flutter**: flutter_test (widget tests), integration_test (E2E), golden tests
- **React Native**: Jest (unit tests), Detox (E2E), React Native Testing Library
- **Appium**: Cross-platform E2E testing (supports iOS, Android, Flutter, React Native)

## Accessibility (A11y)

### iOS Accessibility

- **VoiceOver**: Screen reader, accessibility labels, hints, traits
- **Dynamic Type**: Support text size adjustments
- **Voice Control**: Voice commands for UI navigation
- **Accessibility Inspector**: Testing tool

### Android Accessibility

- **TalkBack**: Screen reader, content descriptions, labels
- **Switch Access**: External switch devices
- **Accessibility Scanner**: Automated testing tool

### Guidelines

- **WCAG 2.1**: Apply to mobile (color contrast, touch targets, labels)
- **Platform Guidelines**: iOS Human Interface Guidelines, Material Design Accessibility

## Related Skills

- [/frontend-engineering](../frontend-engineering/SKILL.md) — React, Flutter UI patterns, and web testing reference when work crosses into web or shared Flutter code
- [/auth-engineering](../auth-engineering/SKILL.md) — token storage, biometric auth flows, and federated access (delegate auth design to identity-security-developer)
- [/api-design](../api-design/SKILL.md) — backend API contracts the mobile app consumes
- [/threat-model](../threat-model/SKILL.md) — STRIDE threat modeling for new attack surface (secure storage, deep links, pinning)
- [/run-quality-checks](../run-quality-checks/SKILL.md) — full pre-commit quality gate
- [/dependency-review](../dependency-review/SKILL.md) — vet SDK and package upgrades for breaking changes and CVEs
