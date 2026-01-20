#!/bin/bash
# PostgreSQL 18 AIO Benchmark Script
# ===================================
# Compares performance between sync, worker, and io_uring modes.
#
# Requirements:
# - PostgreSQL 18 running in Docker
# - Database with existing data (for realistic benchmarks)
# - pgbench installed (comes with postgres container)

set -e

# Configuration
CONTAINER="${CONTAINER:-booru-sql-1}"
DB_USER="${POSTGRES_USER:-szurubooru}"
DB_NAME="${POSTGRES_DB:-$DB_USER}"
RESULTS_DIR="${RESULTS_DIR:-./benchmark-results}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Benchmark parameters
WARMUP_TIME=30
BENCHMARK_TIME=60
CLIENTS=10
THREADS=2

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +%H:%M:%S)]${NC} $1"
}

header() {
    echo
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo
}

# Create results directory
mkdir -p "$RESULTS_DIR"

# Get current io_method
get_io_method() {
    docker exec "$CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c \
        "SHOW io_method;" 2>/dev/null | tr -d ' '
}

# Set io_method (requires postgresql.conf change and restart)
set_io_method() {
    local method=$1
    log "Setting io_method to: $method"

    # Update config
    docker exec "$CONTAINER" bash -c "
        sed -i 's/^io_method = .*/io_method = $method/' /var/lib/postgresql/18/docker/postgresql.conf
    " 2>/dev/null || {
        docker exec "$CONTAINER" bash -c "
            echo 'io_method = $method' >> /var/lib/postgresql/data/postgresql.conf
        "
    }

    # Restart PostgreSQL
    log "Restarting PostgreSQL..."
    docker restart "$CONTAINER"

    # Wait for ready
    for i in {1..30}; do
        if docker exec "$CONTAINER" pg_isready -U "$DB_USER" &>/dev/null; then
            break
        fi
        sleep 2
    done

    log "Current io_method: $(get_io_method)"
}

# Clear OS cache (requires root on host)
clear_cache() {
    log "Attempting to clear OS cache..."
    # This only works if running with sufficient privileges
    sync
    sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches' 2>/dev/null || {
        log "Warning: Could not clear OS cache (need root privileges)"
    }
}

# Run pgbench
run_pgbench() {
    local mode=$1
    local result_file="${RESULTS_DIR}/pgbench_${mode}_${TIMESTAMP}.txt"

    header "Running pgbench benchmark - $mode mode"

    log "Warming up database cache..."
    docker exec "$CONTAINER" pgbench \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -c "$CLIENTS" \
        -j "$THREADS" \
        -T "$WARMUP_TIME" \
        -P 10 \
        > /dev/null 2>&1 || true

    log "Running benchmark for ${BENCHMARK_TIME}s with ${CLIENTS} clients..."
    docker exec "$CONTAINER" pgbench \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -c "$CLIENTS" \
        -j "$THREADS" \
        -T "$BENCHMARK_TIME" \
        -P 10 \
        --progress-timestamp \
        2>&1 | tee "$result_file"

    log "Results saved to: $result_file"
}

# Run custom SQL benchmarks (more realistic for booru workload)
run_custom_benchmarks() {
    local mode=$1
    local result_file="${RESULTS_DIR}/custom_${mode}_${TIMESTAMP}.txt"

    header "Running custom SQL benchmarks - $mode mode"

    echo "=== Custom Benchmark Results for io_method=$mode ===" > "$result_file"
    echo "Timestamp: $(date)" >> "$result_file"
    echo "" >> "$result_file"

    # Sequential scan benchmark (benefits most from AIO)
    log "Test 1: Sequential scan on large table..."
    echo "=== Test 1: Sequential Scan ===" >> "$result_file"

    # Clear buffer cache in PostgreSQL
    docker exec "$CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c \
        "DISCARD ALL;" > /dev/null 2>&1

    for i in {1..5}; do
        START_TIME=$(date +%s%3N)
        docker exec "$CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c \
            "EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
             SELECT COUNT(*) FROM post;" >> "$result_file" 2>&1
        END_TIME=$(date +%s%3N)
        ELAPSED=$((END_TIME - START_TIME))
        echo "Run $i: ${ELAPSED}ms" | tee -a "$result_file"
    done

    # Tag search benchmark (common operation)
    log "Test 2: Tag-based post search..."
    echo "" >> "$result_file"
    echo "=== Test 2: Tag Search ===" >> "$result_file"

    for i in {1..5}; do
        START_TIME=$(date +%s%3N)
        docker exec "$CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c \
            "EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
             SELECT p.id, p.creation_time
             FROM post p
             JOIN post_tag pt ON p.id = pt.post_id
             JOIN tag t ON pt.tag_id = t.id
             WHERE t.first_name LIKE 'a%'
             ORDER BY p.creation_time DESC
             LIMIT 50;" >> "$result_file" 2>&1
        END_TIME=$(date +%s%3N)
        ELAPSED=$((END_TIME - START_TIME))
        echo "Run $i: ${ELAPSED}ms" | tee -a "$result_file"
    done

    # Complex aggregation benchmark
    log "Test 3: Complex aggregation..."
    echo "" >> "$result_file"
    echo "=== Test 3: Complex Aggregation ===" >> "$result_file"

    for i in {1..5}; do
        START_TIME=$(date +%s%3N)
        docker exec "$CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c \
            "EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
             SELECT t.first_name, COUNT(pt.post_id) as post_count
             FROM tag t
             LEFT JOIN post_tag pt ON t.id = pt.tag_id
             GROUP BY t.id, t.first_name
             ORDER BY post_count DESC
             LIMIT 100;" >> "$result_file" 2>&1
        END_TIME=$(date +%s%3N)
        ELAPSED=$((END_TIME - START_TIME))
        echo "Run $i: ${ELAPSED}ms" | tee -a "$result_file"
    done

    # Cold cache benchmark (most important for AIO)
    log "Test 4: Cold cache sequential scan..."
    echo "" >> "$result_file"
    echo "=== Test 4: Cold Cache Scan ===" >> "$result_file"

    # Try to clear PostgreSQL shared buffers
    docker exec "$CONTAINER" psql -U "$DB_USER" -d postgres -c \
        "SELECT pg_prewarm('post', 'buffer', 'main', NULL, NULL);" > /dev/null 2>&1 || true
    docker restart "$CONTAINER"

    # Wait for ready
    for i in {1..30}; do
        if docker exec "$CONTAINER" pg_isready -U "$DB_USER" &>/dev/null; then
            break
        fi
        sleep 2
    done
    sleep 5

    START_TIME=$(date +%s%3N)
    docker exec "$CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c \
        "EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
         SELECT COUNT(*), AVG(file_size) FROM post;" >> "$result_file" 2>&1
    END_TIME=$(date +%s%3N)
    ELAPSED=$((END_TIME - START_TIME))
    echo "Cold cache scan: ${ELAPSED}ms" | tee -a "$result_file"

    log "Results saved to: $result_file"
}

# Initialize pgbench tables
init_pgbench() {
    log "Initializing pgbench tables..."
    docker exec "$CONTAINER" pgbench \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -i \
        -s 10 \
        2>&1 || log "pgbench init may have failed (tables might exist)"
}

# Generate comparison report
generate_report() {
    local report_file="${RESULTS_DIR}/comparison_report_${TIMESTAMP}.txt"

    header "Generating Comparison Report"

    echo "=== PostgreSQL 18 AIO Mode Comparison Report ===" > "$report_file"
    echo "Generated: $(date)" >> "$report_file"
    echo "Server: $(docker exec "$CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c 'SELECT version();')" >> "$report_file"
    echo "" >> "$report_file"
    echo "Configuration:" >> "$report_file"
    echo "- Clients: $CLIENTS" >> "$report_file"
    echo "- Threads: $THREADS" >> "$report_file"
    echo "- Benchmark duration: ${BENCHMARK_TIME}s" >> "$report_file"
    echo "" >> "$report_file"

    # Extract TPS from pgbench results
    echo "=== pgbench Results (TPS) ===" >> "$report_file"
    for mode in sync worker io_uring; do
        RESULT_FILE="${RESULTS_DIR}/pgbench_${mode}_${TIMESTAMP}.txt"
        if [ -f "$RESULT_FILE" ]; then
            TPS=$(grep "tps = " "$RESULT_FILE" | tail -1 | awk '{print $3}')
            echo "$mode: $TPS TPS" >> "$report_file"
        fi
    done

    echo "" >> "$report_file"
    echo "=== Recommendation ===" >> "$report_file"
    echo "Compare the TPS values above. Higher is better." >> "$report_file"
    echo "For network-attached storage (DigitalOcean), 'worker' often performs better." >> "$report_file"
    echo "For local NVMe SSD, 'io_uring' typically wins." >> "$report_file"

    cat "$report_file"
    log "Report saved to: $report_file"
}

# Main benchmark routine
main() {
    header "PostgreSQL 18 AIO Benchmark Suite"

    case "${1:-}" in
        --quick)
            # Quick test with current settings
            log "Running quick benchmark with current io_method..."
            mode=$(get_io_method)
            run_custom_benchmarks "$mode"
            ;;
        --full)
            # Full comparison of all modes
            log "Running full benchmark suite (this will take ~15 minutes)..."

            # Initialize pgbench
            init_pgbench

            # Test each mode
            for mode in sync worker io_uring; do
                set_io_method "$mode"
                sleep 5  # Let system stabilize
                run_pgbench "$mode"
                run_custom_benchmarks "$mode"
            done

            generate_report
            ;;
        --mode)
            # Test specific mode
            if [ -z "${2:-}" ]; then
                echo "Usage: $0 --mode [sync|worker|io_uring]"
                exit 1
            fi
            set_io_method "$2"
            init_pgbench
            run_pgbench "$2"
            run_custom_benchmarks "$2"
            ;;
        *)
            echo "PostgreSQL 18 AIO Benchmark Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --quick         Run quick benchmark with current io_method"
            echo "  --full          Run full comparison of all AIO modes"
            echo "  --mode MODE     Test specific mode (sync|worker|io_uring)"
            echo ""
            echo "Environment variables:"
            echo "  CONTAINER       PostgreSQL container name (default: booru-sql-1)"
            echo "  POSTGRES_USER   Database user"
            echo "  POSTGRES_DB     Database name"
            echo "  RESULTS_DIR     Directory for results (default: ./benchmark-results)"
            ;;
    esac
}

main "$@"
