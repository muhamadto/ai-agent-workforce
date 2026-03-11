---
name: db-migration-review
description: Review database migration scripts for safety, reversibility, performance impact, and correctness before applying to production.
---

# DB Migration Review Skill

Review database migration scripts (Flyway, Liquibase, raw SQL) for safety, data integrity, and production readiness before they are applied.

## When to use

- A new migration script has been written and needs a safety review
- Reviewing a teammate's migration in a PR
- Before running migrations on a staging or production database

---

## Step 1 — Locate migration files

```bash
find . -path "*/db/migration/*.sql" -o \
       -path "*/resources/db/migration/*.sql" -o \
       -path "*/changelog/*.xml" -o \
       -path "*/changelog/*.yaml" 2>/dev/null | sort
```

## Step 2 — Read each migration

For every migration file, check the following categories:

---

### Category 1: Destructive operations

Flag immediately — require explicit confirmation before proceeding:

| Operation | Risk |
|-----------|------|
| `DROP TABLE` | Permanent data loss |
| `DROP COLUMN` | Permanent data loss |
| `TRUNCATE` | All rows deleted |
| `DELETE` without `WHERE` | All rows deleted |
| `ALTER TABLE ... DROP CONSTRAINT` | Referential integrity broken |

**Check:**

```bash
grep -iEn "DROP\s+(TABLE|COLUMN|INDEX|CONSTRAINT)|TRUNCATE|DELETE\s+FROM\s+\w+\s*;" \
  <migration-file>
```

If found: confirm the operation is intentional, there is a rollback plan, and data has been backed up.

---

### Category 2: Lock-heavy operations

These acquire `ACCESS EXCLUSIVE` locks (PostgreSQL) that block reads and writes:

| Operation | Safe alternative |
|-----------|-----------------|
| `ALTER TABLE ... ADD COLUMN NOT NULL` without default | Add column nullable first, backfill, then add constraint |
| `ALTER TABLE ... ADD CONSTRAINT` | Use `NOT VALID` + `VALIDATE CONSTRAINT` in a separate migration |
| `CREATE INDEX` without `CONCURRENTLY` | Use `CREATE INDEX CONCURRENTLY` |
| `ALTER TABLE ... ALTER COLUMN TYPE` | Depends — shadow column pattern for large tables |

**Check:**

```bash
grep -iEn "ADD\s+COLUMN|ALTER\s+COLUMN|ADD\s+CONSTRAINT|CREATE\s+INDEX" \
  <migration-file> | grep -iv "CONCURRENTLY"
```

For tables > 1M rows, any lock-heavy operation is a production risk.

---

### Category 3: Missing rollback / undo

Every migration should be reversible. Check for a corresponding rollback section:

- **Flyway**: Look for a corresponding `U__<version>__<name>.sql` undo script
- **Liquibase**: Check that every `changeSet` has a `rollback` block
- **Raw SQL**: Is there a companion `down.sql` or rollback script?

If rollback is missing, document the manual rollback steps in a comment at the top of the migration.

---

### Category 4: Data migrations mixed with schema changes

Never mix data and schema changes in the same migration — they have different failure modes and rollback strategies.

**Flag if a single migration contains both:**
- DDL (`CREATE`, `ALTER`, `DROP`)
- DML (`INSERT`, `UPDATE`, `DELETE`)

Recommend splitting into separate migrations.

---

### Category 5: Performance — large table operations

```bash
# Check if the table being altered is large
grep -iE "ALTER TABLE|DROP COLUMN|ADD COLUMN|CREATE INDEX" <migration-file>
```

For any `ALTER TABLE` on a table with > 1M rows:
- Add column as nullable first, then backfill in batches, then add `NOT NULL`
- Use `CREATE INDEX CONCURRENTLY` in PostgreSQL
- Wrap batched `UPDATE` in transactions of ≤ 10,000 rows

---

### Category 6: Naming and conventions

- Migration files must follow the project naming convention (e.g. `V001__create_users.sql`)
- Table and column names use `snake_case`
- Foreign key constraint names include both table names: `fk_orders_users`
- Index names include table and column(s): `idx_orders_user_id`

---

## Step 3 — Output the review

Produce a structured review:

```text
## DB Migration Review: <filename>

### Summary
<one-line description of what the migration does>

### Risk Level
🟢 Low | 🟡 Medium | 🔴 High

### Findings

| # | Category | Finding | Recommendation |
|---|----------|---------|----------------|
| 1 | Lock-heavy | CREATE INDEX without CONCURRENTLY | Use CREATE INDEX CONCURRENTLY |
| 2 | No rollback | No undo script found | Add U__<version>__<name>.sql |

### Approval
- [ ] Destructive operations confirmed with data backup plan
- [ ] Lock-heavy ops use safe alternatives for large tables
- [ ] Rollback script exists or manual steps documented
- [ ] Data and schema changes are in separate migrations
- [ ] Naming conventions followed
```

---

## Safety rules

- Never run a migration review on a production database without a backup confirmed
- Never approve a migration that drops a column without verifying no application code references it
- Never approve `CREATE INDEX` without `CONCURRENTLY` on a live table > 100K rows
- If risk is 🔴 High, escalate to the team lead before approving
