# Git Hooks Quality Gate Guide

## Overview

Three git hooks enforce code quality and Conventional Commits:

1. **pre-commit**: Fast checks before commit (tests, formatting, coverage)
2. **pre-push**: SonarQube analysis before push (quality gate)
3. **commit-msg**: Validate Conventional Commits format

## Installation

### For New Repositories
```bash
git init  # Hooks auto-installed from ~/.git-templates/
```

### For Existing Repositories
```bash
cd /path/to/repo
cp ~/.git-templates/hooks/* .git/hooks/
chmod +x .git/hooks/*
```

## Hook Details

### 1. Pre-Commit Hook (Fast - ~30 seconds)

**Runs before each commit:**
- ✅ Code formatting check (`mvn spotless:check`)
- ✅ Unit tests (`mvn test`)
- ✅ Test coverage check (≥90% required via JaCoCo)
- ✅ Checkstyle validation
- ✅ Conventional commit format validation

**If it fails:**
```bash
# Fix formatting
mvn spotless:apply

# Run tests
mvn test

# Check coverage
mvn jacoco:report
# View: target/site/jacoco/index.html

# Fix issues and retry commit
```

**Bypass (NOT RECOMMENDED):**
```bash
git commit --no-verify
```

### 2. Pre-Push Hook (Comprehensive - ~2-5 minutes)

**Runs before push to remote:**
- ✅ Full test suite (`mvn verify`)
- ✅ SonarQube analysis
- ✅ Quality gate enforcement:
  - Code coverage ≥90%
  - No critical bugs
  - No security vulnerabilities
  - Code quality standards met

**Prerequisites:**
```bash
# Set SonarQube token (required)
export SONAR_TOKEN=your-sonarqube-token

# Or add to ~/.zshrc for persistence
echo 'export SONAR_TOKEN=your-token' >> ~/.zshrc
```

**If SonarQube quality gate fails:**
1. View detailed report: http://localhost:9000
2. Fix issues (bugs, vulnerabilities, coverage)
3. Run locally: `mvn verify sonar:sonar -Pcoverage`
4. Retry push when quality gate passes

**Bypass (NOT RECOMMENDED):**
```bash
git push --no-verify
```

### 3. Commit-Msg Hook (Instant)

**Validates commit message format:**
- ✅ Must follow Conventional Commits
- ✅ Type is required (feat, fix, docs, etc.)
- ✅ Lowercase description
- ✅ Max 72 characters
- ⚠️  Warns if missing Co-Authored-By (non-blocking)

**Valid formats:**
```bash
feat(auth): add OAuth2 login
fix(api): prevent race condition
docs: update authentication guide
```

**Invalid formats:**
```bash
Add OAuth2           # Missing type
feat:add OAuth2      # Missing space
feat: Add OAuth2     # Uppercase
feat: add oauth2.    # Period at end
```

## Maven Configuration Required

Add to your `pom.xml`:

### 1. JaCoCo Plugin (Code Coverage)
```xml
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.11</version>
    <executions>
        <execution>
            <id>prepare-agent</id>
            <goals><goal>prepare-agent</goal></goals>
        </execution>
        <execution>
            <id>report</id>
            <phase>test</phase>
            <goals><goal>report</goal></goals>
        </execution>
        <execution>
            <id>jacoco-check</id>
            <phase>verify</phase>
            <goals><goal>check</goal></goals>
            <configuration>
                <rules>
                    <rule>
                        <element>PACKAGE</element>
                        <limits>
                            <limit>
                                <counter>LINE</counter>
                                <value>COVEREDRATIO</value>
                                <minimum>0.90</minimum>
                            </limit>
                        </limits>
                    </rule>
                </rules>
            </configuration>
        </execution>
    </executions>
</plugin>
```

### 2. Spotless Plugin (Code Formatting)
```xml
<plugin>
    <groupId>com.diffplug.spotless</groupId>
    <artifactId>spotless-maven-plugin</artifactId>
    <version>2.43.0</version>
    <configuration>
        <java>
            <googleJavaFormat>
                <version>1.19.2</version>
                <style>GOOGLE</style>
            </googleJavaFormat>
        </java>
    </configuration>
</plugin>
```

### 3. SonarQube Properties
```xml
<properties>
    <sonar.host.url>http://localhost:9000</sonar.host.url>
    <sonar.qualitygate.wait>true</sonar.qualitygate.wait>
    <sonar.coverage.jacoco.xmlReportPaths>
        ${project.build.directory}/site/jacoco/jacoco.xml
    </sonar.coverage.jacoco.xmlReportPaths>
</properties>
```

**Full example:** See `roles/ai/files/maven/pom-quality-profile.xml`

## Workflow Examples

### Successful Commit & Push
```bash
# Make changes
vim src/main/java/MyClass.java

# Format code
mvn spotless:apply

# Run tests
mvn test

# Commit (pre-commit hook runs automatically)
git commit -m "feat(api): add user authentication endpoint"
# ✅ Code formatting passed
# ✅ Unit tests passed
# ✅ Test coverage: 92%
# ✅ Commit message format valid

# Push (pre-push hook runs automatically)
git push
# ⚠️  About to push. Running quality gate...
# 📊 Running SonarQube analysis...
# ✅ SonarQube quality gate PASSED
# ✅ Pushed to remote
```

### Failed Commit (Coverage < 90%)
```bash
git commit -m "feat: add feature"
# 🧪 Running unit tests...
# ✅ Unit tests passed
# 📊 Checking test coverage...
# ❌ Test coverage is 85%, minimum required is 90%

# Fix: Add more tests
vim src/test/java/MyClassTest.java

# Verify coverage
mvn jacoco:report
open target/site/jacoco/index.html

# Retry commit
git commit -m "feat: add feature"
# ✅ Test coverage: 91%
```

### Failed Push (SonarQube Quality Gate)
```bash
git push
# 📊 Running SonarQube analysis...
# ❌ SonarQube quality gate FAILED
#    - Code coverage: 88% (required: 90%)
#    - 2 critical bugs detected
#    - 1 security vulnerability
#
#    View report: http://localhost:9000

# Fix issues, then retry
mvn verify sonar:sonar -Pcoverage
git push
```

## Configuration

### Skip Hooks Temporarily
```bash
# Skip pre-commit
git commit --no-verify

# Skip pre-push
git push --no-verify
```

### Disable Hooks Permanently (per repo)
```bash
cd /path/to/repo
rm .git/hooks/pre-commit
rm .git/hooks/pre-push
rm .git/hooks/commit-msg
```

### Set SonarQube Token
```bash
# Temporary (current session)
export SONAR_TOKEN=squ_1234567890abcdef

# Permanent (add to ~/.zshrc)
echo 'export SONAR_TOKEN=squ_1234567890abcdef' >> ~/.zshrc
source ~/.zshrc
```

### Customize Coverage Threshold
Edit `.git/hooks/pre-commit`:
```bash
# Change line:
if [ "$COVERAGE" -lt 90 ]; then
# To:
if [ "$COVERAGE" -lt 85 ]; then  # 85% threshold
```

## Troubleshooting

### "mvn: command not found"
```bash
# Install Maven
brew install maven
```

### "SONAR_TOKEN not set"
```bash
# Generate token in SonarQube UI:
# User > My Account > Security > Generate Token

# Set token
export SONAR_TOKEN=your-token
```

### "SonarQube server not reachable"
```bash
# Start SonarQube (if running locally)
docker run -d -p 9000:9000 sonarqube:latest

# Or point to remote server
export SONAR_HOST_URL=https://sonarqube.example.com
```

### Pre-commit too slow?
```bash
# Run only formatting check (skip tests)
# Edit .git/hooks/pre-commit and comment out test section
```

## Best Practices

1. **Run checks locally before committing:**
   ```bash
   mvn clean verify
   ```

2. **Format code automatically:**
   ```bash
   mvn spotless:apply
   ```

3. **Check coverage regularly:**
   ```bash
   mvn jacoco:report
   open target/site/jacoco/index.html
   ```

4. **Use Conventional Commits:**
   - `feat:` for new features
   - `fix:` for bug fixes
   - `refactor:` for code refactoring
   - `test:` for test additions
   - `docs:` for documentation

5. **Never use `--no-verify` without good reason:**
   - Quality gates exist to prevent issues
   - Bypassing hooks = technical debt

## Summary

| Hook | When | Duration | Checks | Bypass |
|------|------|----------|--------|--------|
| **pre-commit** | Before commit | ~30s | Tests, formatting, coverage | `--no-verify` |
| **pre-push** | Before push | ~2-5min | SonarQube quality gate | `--no-verify` |
| **commit-msg** | After commit message | <1s | Conventional format | Edit message |

**Quality Standards:**
- ✅ Code coverage ≥90%
- ✅ All tests passing
- ✅ Code formatted (Google Java Style)
- ✅ No critical bugs or vulnerabilities
- ✅ Conventional Commits format
- ✅ SonarQube quality gate passed
