#!/bin/bash
# HTTP Server Benchmark Script
# ============================
# Compares performance between waitress and granian HTTP servers.
#
# Requirements:
# - wrk or ab (Apache Benchmark) installed
# - Application running on specified port
# - Database with test data

set -e

# Configuration
HOST="${HOST:-localhost}"
PORT="${PORT:-6666}"
RESULTS_DIR="${RESULTS_DIR:-./benchmark-results}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Benchmark parameters
DURATION=30
CONNECTIONS=100
THREADS=4

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

mkdir -p "$RESULTS_DIR"

# Check for benchmarking tools
check_tools() {
    if command -v wrk &> /dev/null; then
        BENCH_TOOL="wrk"
        log "Using wrk for benchmarking"
    elif command -v ab &> /dev/null; then
        BENCH_TOOL="ab"
        log "Using Apache Benchmark (ab)"
    elif command -v hey &> /dev/null; then
        BENCH_TOOL="hey"
        log "Using hey for benchmarking"
    else
        log "No benchmarking tool found. Installing wrk..."
        # Try to install wrk
        if command -v brew &> /dev/null; then
            brew install wrk
            BENCH_TOOL="wrk"
        elif command -v apt-get &> /dev/null; then
            sudo apt-get install -y wrk
            BENCH_TOOL="wrk"
        else
            echo "Please install wrk, ab (apache2-utils), or hey"
            echo "  macOS: brew install wrk"
            echo "  Ubuntu: apt-get install wrk"
            echo "  Go: go install github.com/rakyll/hey@latest"
            exit 1
        fi
    fi
}

# Wait for server to be ready
wait_for_server() {
    log "Waiting for server at http://${HOST}:${PORT}..."
    for i in {1..30}; do
        if curl -s "http://${HOST}:${PORT}/api" > /dev/null 2>&1; then
            log "Server is ready"
            return 0
        fi
        sleep 1
    done
    log "Server failed to start"
    exit 1
}

# Run wrk benchmark
run_wrk() {
    local name=$1
    local url=$2
    local result_file="${RESULTS_DIR}/${name}_${TIMESTAMP}.txt"

    log "Running wrk benchmark: $name"
    echo "=== wrk benchmark: $name ===" > "$result_file"
    echo "URL: $url" >> "$result_file"
    echo "Duration: ${DURATION}s, Connections: ${CONNECTIONS}, Threads: ${THREADS}" >> "$result_file"
    echo "" >> "$result_file"

    wrk -t${THREADS} -c${CONNECTIONS} -d${DURATION}s "$url" 2>&1 | tee -a "$result_file"

    log "Results saved to: $result_file"
}

# Run ab benchmark
run_ab() {
    local name=$1
    local url=$2
    local result_file="${RESULTS_DIR}/${name}_${TIMESTAMP}.txt"

    log "Running ab benchmark: $name"
    echo "=== ab benchmark: $name ===" > "$result_file"
    echo "URL: $url" >> "$result_file"
    echo "Total requests: 10000, Concurrency: ${CONNECTIONS}" >> "$result_file"
    echo "" >> "$result_file"

    ab -n 10000 -c ${CONNECTIONS} "$url" 2>&1 | tee -a "$result_file"

    log "Results saved to: $result_file"
}

# Run hey benchmark
run_hey() {
    local name=$1
    local url=$2
    local result_file="${RESULTS_DIR}/${name}_${TIMESTAMP}.txt"

    log "Running hey benchmark: $name"
    echo "=== hey benchmark: $name ===" > "$result_file"
    echo "URL: $url" >> "$result_file"
    echo "Duration: ${DURATION}s, Concurrency: ${CONNECTIONS}" >> "$result_file"
    echo "" >> "$result_file"

    hey -z ${DURATION}s -c ${CONNECTIONS} "$url" 2>&1 | tee -a "$result_file"

    log "Results saved to: $result_file"
}

# Run benchmark based on available tool
run_benchmark() {
    local name=$1
    local url=$2

    case $BENCH_TOOL in
        wrk)
            run_wrk "$name" "$url"
            ;;
        ab)
            run_ab "$name" "$url"
            ;;
        hey)
            run_hey "$name" "$url"
            ;;
    esac
}

# Benchmark API endpoints
benchmark_endpoints() {
    local server_name=$1
    local base_url="http://${HOST}:${PORT}"

    header "Benchmarking ${server_name}"

    # Test 1: API root (lightweight)
    log "Test 1: API root endpoint"
    run_benchmark "${server_name}_api_root" "${base_url}/api"

    # Test 2: Tag list (database read)
    log "Test 2: Tag list endpoint"
    run_benchmark "${server_name}_tags" "${base_url}/api/tags?limit=50"

    # Test 3: Post list (complex query with joins)
    log "Test 3: Post list endpoint"
    run_benchmark "${server_name}_posts" "${base_url}/api/posts?limit=50"

    # Test 4: Post search (search system)
    log "Test 4: Post search endpoint"
    run_benchmark "${server_name}_search" "${base_url}/api/posts?query=*&limit=20"
}

# Generate comparison report
generate_report() {
    local report_file="${RESULTS_DIR}/http_server_comparison_${TIMESTAMP}.txt"

    header "Generating Comparison Report"

    echo "=== HTTP Server Benchmark Comparison ===" > "$report_file"
    echo "Generated: $(date)" >> "$report_file"
    echo "Host: ${HOST}:${PORT}" >> "$report_file"
    echo "Benchmark tool: ${BENCH_TOOL}" >> "$report_file"
    echo "" >> "$report_file"

    # Extract key metrics from each test
    echo "=== Results Summary ===" >> "$report_file"

    for server in waitress granian; do
        echo "" >> "$report_file"
        echo "--- ${server} ---" >> "$report_file"

        for test in api_root tags posts search; do
            result_file="${RESULTS_DIR}/${server}_${test}_${TIMESTAMP}.txt"
            if [ -f "$result_file" ]; then
                echo "  ${test}:" >> "$report_file"
                case $BENCH_TOOL in
                    wrk)
                        grep "Requests/sec" "$result_file" >> "$report_file" 2>/dev/null || true
                        grep "Latency" "$result_file" | head -1 >> "$report_file" 2>/dev/null || true
                        ;;
                    ab)
                        grep "Requests per second" "$result_file" >> "$report_file" 2>/dev/null || true
                        grep "Time per request" "$result_file" | head -1 >> "$report_file" 2>/dev/null || true
                        ;;
                    hey)
                        grep "Requests/sec" "$result_file" >> "$report_file" 2>/dev/null || true
                        grep "Average:" "$result_file" >> "$report_file" 2>/dev/null || true
                        ;;
                esac
            fi
        done
    done

    echo "" >> "$report_file"
    echo "=== Recommendations ===" >> "$report_file"
    echo "Compare Requests/sec values. Higher is better." >> "$report_file"
    echo "Compare Latency values. Lower is better." >> "$report_file"
    echo "" >> "$report_file"
    echo "For CPU-bound workloads: Both servers similar" >> "$report_file"
    echo "For I/O-bound workloads: Granian typically wins" >> "$report_file"
    echo "For memory efficiency: Granian uses less memory per worker" >> "$report_file"

    cat "$report_file"
    log "Report saved to: $report_file"
}

# Switch server implementation
switch_server() {
    local server=$1

    log "Switching to ${server}..."

    # This assumes docker-compose setup
    if [ "$server" == "waitress" ]; then
        # Use default docker-start.sh
        docker compose -f docker-compose.dev.yml exec server bash -c "
            pkill -f 'granian|waitress' || true
            /opt/app/docker-start.sh &
        " 2>/dev/null || {
            log "Note: Run this with server already running the specified server type"
        }
    elif [ "$server" == "granian" ]; then
        # Use granian startup script
        docker compose -f docker-compose.dev.yml exec server bash -c "
            pkill -f 'granian|waitress' || true
            /opt/app/docker-start-granian.sh &
        " 2>/dev/null || {
            log "Note: Run this with server already running the specified server type"
        }
    fi

    sleep 5
}

# Main execution
main() {
    header "HTTP Server Benchmark Suite"

    case "${1:-}" in
        --quick)
            # Quick test against current running server
            check_tools
            wait_for_server
            benchmark_endpoints "current"
            ;;
        --full)
            # Full comparison (requires manual server restarts)
            check_tools

            echo "This benchmark requires manually switching between server implementations."
            echo ""
            echo "Step 1: Start the server with waitress (default docker-start.sh)"
            echo "Step 2: Run: $0 --benchmark waitress"
            echo "Step 3: Restart server with granian (docker-start-granian.sh)"
            echo "Step 4: Run: $0 --benchmark granian"
            echo "Step 5: Run: $0 --report"
            ;;
        --benchmark)
            if [ -z "${2:-}" ]; then
                echo "Usage: $0 --benchmark [waitress|granian]"
                exit 1
            fi
            check_tools
            wait_for_server
            benchmark_endpoints "$2"
            ;;
        --report)
            generate_report
            ;;
        *)
            echo "HTTP Server Benchmark Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --quick              Benchmark current running server"
            echo "  --full               Show full comparison instructions"
            echo "  --benchmark SERVER   Benchmark specific server (waitress|granian)"
            echo "  --report             Generate comparison report from existing results"
            echo ""
            echo "Environment variables:"
            echo "  HOST           Server host (default: localhost)"
            echo "  PORT           Server port (default: 6666)"
            echo "  RESULTS_DIR    Directory for results (default: ./benchmark-results)"
            echo "  DURATION       Benchmark duration in seconds (default: 30)"
            echo "  CONNECTIONS    Concurrent connections (default: 100)"
            echo ""
            echo "Example workflow:"
            echo "  1. Start server with waitress: ./d"
            echo "  2. Run: $0 --benchmark waitress"
            echo "  3. Restart server with granian"
            echo "  4. Run: $0 --benchmark granian"
            echo "  5. Run: $0 --report"
            ;;
    esac
}

main "$@"
