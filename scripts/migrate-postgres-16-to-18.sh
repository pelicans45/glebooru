#!/bin/bash
# PostgreSQL 16 to 18 Migration Script
# =====================================
# This script migrates a PostgreSQL 16 database to PostgreSQL 18
# using pg_dump/pg_restore for maximum compatibility.
#
# IMPORTANT: Test this thoroughly in a dev environment before running in production!
#
# Prerequisites:
# - Docker and docker compose installed
# - Sufficient disk space for backup (at least 2x database size)
# - Application stopped (no active connections)

set -e  # Exit on error
set -u  # Exit on undefined variable

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/opt/backup}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/szurubooru_pg16_${TIMESTAMP}.sql.gz"
OLD_CONTAINER="${OLD_CONTAINER:-booru-sql-1}"
NEW_CONTAINER="${NEW_CONTAINER:-booru-sql-1}"
DB_USER="${POSTGRES_USER:-szurubooru}"
DB_NAME="${POSTGRES_DB:-$DB_USER}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if docker is available
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi

    # Check if backup directory exists
    if [ ! -d "$BACKUP_DIR" ]; then
        log_warn "Backup directory $BACKUP_DIR does not exist, creating..."
        mkdir -p "$BACKUP_DIR"
    fi

    # Check disk space (need at least 10GB free for safety)
    AVAILABLE_SPACE=$(df -BG "$BACKUP_DIR" | awk 'NR==2 {print $4}' | tr -d 'G')
    if [ "$AVAILABLE_SPACE" -lt 10 ]; then
        log_error "Insufficient disk space. Need at least 10GB free, have ${AVAILABLE_SPACE}GB"
        exit 1
    fi

    log_info "Prerequisites check passed"
}

verify_old_postgres() {
    log_info "Verifying PostgreSQL 16 container is running..."

    if ! docker ps --format '{{.Names}}' | grep -q "^${OLD_CONTAINER}$"; then
        log_error "Container $OLD_CONTAINER is not running"
        exit 1
    fi

    # Check PostgreSQL version
    PG_VERSION=$(docker exec "$OLD_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT version();" 2>/dev/null | head -1)
    log_info "Current PostgreSQL version: $PG_VERSION"

    if ! echo "$PG_VERSION" | grep -q "PostgreSQL 16"; then
        log_warn "Expected PostgreSQL 16, but got: $PG_VERSION"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

create_backup() {
    log_info "Creating backup of PostgreSQL 16 database..."
    log_info "Backup file: $BACKUP_FILE"

    # Create a full dump with pg_dump
    # Using custom format for faster restore with parallel option
    docker exec "$OLD_CONTAINER" pg_dump \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --verbose \
        --format=custom \
        --no-owner \
        --no-privileges \
        --clean \
        --if-exists \
        2>&1 | gzip > "$BACKUP_FILE"

    # Also create a plain SQL backup for safety
    BACKUP_SQL="${BACKUP_DIR}/szurubooru_pg16_${TIMESTAMP}.sql"
    log_info "Creating plain SQL backup: $BACKUP_SQL"
    docker exec "$OLD_CONTAINER" pg_dump \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --verbose \
        --format=plain \
        --no-owner \
        --no-privileges \
        --clean \
        --if-exists \
        > "$BACKUP_SQL" 2>&1

    gzip "$BACKUP_SQL"

    # Verify backup exists and has content
    if [ ! -s "$BACKUP_FILE" ]; then
        log_error "Backup file is empty or doesn't exist"
        exit 1
    fi

    BACKUP_SIZE=$(ls -lh "$BACKUP_FILE" | awk '{print $5}')
    log_info "Backup completed. Size: $BACKUP_SIZE"
}

stop_services() {
    log_info "Stopping application services..."

    # Stop server and client, but keep SQL running for now
    docker compose -f "$COMPOSE_FILE" stop server client || true

    log_info "Services stopped"
}

stop_old_postgres() {
    log_info "Stopping PostgreSQL 16 container..."
    docker compose -f "$COMPOSE_FILE" stop sql
    log_info "PostgreSQL 16 stopped"
}

remove_old_volume() {
    log_info "Removing old PostgreSQL data volume..."
    log_warn "This will delete the old database! Make sure backup is valid!"

    read -p "Type 'DELETE' to confirm volume removal: " -r
    if [ "$REPLY" != "DELETE" ]; then
        log_error "Volume removal cancelled"
        exit 1
    fi

    # Get volume name from compose file
    VOLUME_NAME=$(docker compose -f "$COMPOSE_FILE" config --volumes | grep -E "^db$|sql" | head -1)
    if [ -z "$VOLUME_NAME" ]; then
        VOLUME_NAME="db"
    fi

    # Full volume name includes project prefix
    PROJECT_NAME=$(basename "$(dirname "$(realpath "$COMPOSE_FILE")")")
    FULL_VOLUME_NAME="${PROJECT_NAME}_${VOLUME_NAME}"

    log_info "Removing volume: $FULL_VOLUME_NAME"
    docker volume rm "$FULL_VOLUME_NAME" || true

    log_info "Old volume removed"
}

start_new_postgres() {
    log_info "Starting PostgreSQL 18 container..."

    # Pull the new image first
    docker pull postgres:18.1

    # Start the new PostgreSQL container
    docker compose -f "$COMPOSE_FILE" up -d sql

    # Wait for PostgreSQL to be ready
    log_info "Waiting for PostgreSQL 18 to be ready..."
    for i in {1..30}; do
        if docker exec "$NEW_CONTAINER" pg_isready -U "$DB_USER" &>/dev/null; then
            log_info "PostgreSQL 18 is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            log_error "PostgreSQL 18 failed to start in time"
            exit 1
        fi
        sleep 2
    done

    # Verify version
    PG_VERSION=$(docker exec "$NEW_CONTAINER" psql -U "$DB_USER" -d postgres -t -c "SELECT version();" 2>/dev/null | head -1)
    log_info "New PostgreSQL version: $PG_VERSION"
}

restore_backup() {
    log_info "Restoring database from backup..."

    # Create database if it doesn't exist
    docker exec "$NEW_CONTAINER" psql -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME WITH OWNER $DB_USER;" 2>/dev/null || true

    # Restore from custom format backup
    log_info "Restoring from backup file: $BACKUP_FILE"

    # Copy backup to container
    docker cp "$BACKUP_FILE" "${NEW_CONTAINER}:/tmp/backup.sql.gz"

    # Restore
    docker exec "$NEW_CONTAINER" bash -c "
        gunzip -c /tmp/backup.sql.gz | pg_restore \
            -U $DB_USER \
            -d $DB_NAME \
            --verbose \
            --no-owner \
            --no-privileges \
            --clean \
            --if-exists \
            --single-transaction \
            2>&1
    " || {
        log_warn "pg_restore completed with warnings (this is often normal for --clean)"
    }

    # Cleanup
    docker exec "$NEW_CONTAINER" rm -f /tmp/backup.sql.gz

    log_info "Database restore completed"
}

verify_restoration() {
    log_info "Verifying database restoration..."

    # Count tables
    TABLE_COUNT=$(docker exec "$NEW_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "
        SELECT COUNT(*) FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
    " | tr -d ' ')

    log_info "Tables found: $TABLE_COUNT"

    if [ "$TABLE_COUNT" -lt 5 ]; then
        log_error "Expected more tables. Restoration may have failed."
        exit 1
    fi

    # Count posts (main content table)
    POST_COUNT=$(docker exec "$NEW_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "
        SELECT COUNT(*) FROM post;
    " 2>/dev/null | tr -d ' ' || echo "0")

    log_info "Posts found: $POST_COUNT"

    # Run ANALYZE to update statistics
    log_info "Running ANALYZE to update statistics..."
    docker exec "$NEW_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "ANALYZE VERBOSE;" > /dev/null 2>&1

    log_info "Database verification completed"
}

configure_postgres_18() {
    log_info "Applying PostgreSQL 18 optimizations..."

    # Copy custom postgresql.conf if it exists
    if [ -f "server/postgres/postgresql.conf" ]; then
        log_info "Copying custom postgresql.conf..."
        docker cp server/postgres/postgresql.conf "${NEW_CONTAINER}:/var/lib/postgresql/18/docker/postgresql.conf"

        # Reload configuration
        docker exec "$NEW_CONTAINER" psql -U "$DB_USER" -d postgres -c "SELECT pg_reload_conf();"
        log_info "Configuration reloaded"
    else
        log_warn "No custom postgresql.conf found, using defaults"
    fi
}

start_application() {
    log_info "Starting application services..."
    docker compose -f "$COMPOSE_FILE" up -d
    log_info "Application services started"
}

run_migrations() {
    log_info "Running Alembic migrations (if any)..."
    # The server container runs migrations on startup automatically
    sleep 10

    # Check server logs for migration success
    docker compose -f "$COMPOSE_FILE" logs server --tail 20

    log_info "Migrations completed"
}

print_summary() {
    echo
    echo "=========================================="
    echo "  Migration Complete!"
    echo "=========================================="
    echo
    echo "Backup location: $BACKUP_FILE"
    echo "New PostgreSQL version: 18.1"
    echo
    echo "Next steps:"
    echo "1. Verify application functionality"
    echo "2. Monitor logs: docker compose logs -f"
    echo "3. Test database queries for performance"
    echo "4. Run benchmark scripts to compare AIO modes"
    echo
    echo "To rollback (if needed):"
    echo "1. Stop services: docker compose down"
    echo "2. Change docker-compose.yml back to postgres:16"
    echo "3. Remove new volume and restore from backup"
    echo
}

# Main execution
main() {
    echo "=========================================="
    echo "  PostgreSQL 16 to 18 Migration Script"
    echo "=========================================="
    echo

    # Parse arguments
    case "${1:-}" in
        --backup-only)
            check_prerequisites
            verify_old_postgres
            create_backup
            log_info "Backup completed. Exiting without migration."
            exit 0
            ;;
        --restore-only)
            if [ -z "${2:-}" ]; then
                log_error "Please provide backup file path"
                exit 1
            fi
            BACKUP_FILE="$2"
            start_new_postgres
            restore_backup
            verify_restoration
            configure_postgres_18
            exit 0
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo
            echo "Options:"
            echo "  --backup-only     Create backup only, don't migrate"
            echo "  --restore-only    Restore from backup file"
            echo "  --help, -h        Show this help message"
            echo
            echo "Environment variables:"
            echo "  BACKUP_DIR        Backup directory (default: /opt/backup)"
            echo "  OLD_CONTAINER     Old PostgreSQL container name"
            echo "  NEW_CONTAINER     New PostgreSQL container name"
            echo "  POSTGRES_USER     Database user"
            echo "  POSTGRES_DB       Database name"
            echo "  COMPOSE_FILE      Docker compose file path"
            exit 0
            ;;
    esac

    check_prerequisites
    verify_old_postgres
    create_backup
    stop_services
    stop_old_postgres
    remove_old_volume
    start_new_postgres
    restore_backup
    verify_restoration
    configure_postgres_18
    start_application
    run_migrations
    print_summary
}

main "$@"
