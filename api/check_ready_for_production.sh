#!/bin/bash

# =============================================
# FastAPI - Production Readiness Check
# Purpose: Comprehensive pre-production validation script for FastAPI
# Includes: Security, Code Quality, Performance, Best Practices
# =============================================

# Exit immediately if a command exits with a non-zero status
set -e

# Colors for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; }
step()    { echo -e "${PURPLE}[STEP]${NC} $1"; }
check()   { echo -e "${CYAN}[CHECK]${NC} $1"; }

# Global variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
VENV_PATH="$PROJECT_ROOT/../env/bin/activate"
ENV_FILE="$PROJECT_ROOT/../.env"
REPORTS_DIR="$PROJECT_ROOT/production_check_reports"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
PROJECT_NAME="FastAPI-Backend"

# Initialize counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

# Function to increment counters
increment_check() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
}

increment_pass() {
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
}

increment_fail() {
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
}

increment_warning() {
    WARNING_CHECKS=$((WARNING_CHECKS + 1))
}

# Function to print header
print_header() {
    echo -e "\n${PURPLE}=============================================${NC}"
    echo -e "${PURPLE} $PROJECT_NAME - Production Readiness Check${NC}"
    echo -e "${PURPLE}=============================================${NC}\n"
    info "Script Directory: $SCRIPT_DIR"
    info "Project Root: $PROJECT_ROOT"
    info "Timestamp: $TIMESTAMP"
    echo -e "\n"
}

# Function to print footer
print_footer() {
    echo -e "\n${PURPLE}=============================================${NC}"
    echo -e "${PURPLE}📊 Production Readiness Check Summary${NC}"
    echo -e "${PURPLE}=============================================${NC}"
    echo -e "Total Checks: ${BLUE}$TOTAL_CHECKS${NC}"
    echo -e "Passed: ${GREEN}$PASSED_CHECKS${NC}"
    echo -e "Failed: ${RED}$FAILED_CHECKS${NC}"
    echo -e "Warnings: ${YELLOW}$WARNING_CHECKS${NC}"
    
    if [ $FAILED_CHECKS -eq 0 ]; then
        echo -e "\n${GREEN}🎉 All checks passed! Ready for production deployment.${NC}"
        exit 0
    else
        echo -e "\n${RED}❌ Some checks failed. Please fix issues before production deployment.${NC}"
        exit 1
    fi
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Python packages if needed
install_python_package() {
    local package=$1
    if ! python3 -c "import $package" 2>/dev/null; then
        info "Installing $package..."
        pip install "$package" --quiet || {
            error "Failed to install $package"
            return 1
        }
    fi
}

# Step 1: Environment Setup
setup_environment() {
    step "Setting up environment..."
    
    # Check .env file
    increment_check
    if [ ! -f "$ENV_FILE" ]; then
        error "Environment file not found at $ENV_FILE"
        increment_fail
        return 1
    else
        success "Environment file found"
        increment_pass
    fi
    
    # Load environment variables
    info "Loading environment variables from $ENV_FILE"
    set -a
    source "$ENV_FILE" 2>/dev/null || true
    set +a
    success "Environment variables loaded"
    
    # Check virtual environment
    increment_check
    if [ -f "$VENV_PATH" ]; then
        success "Virtual environment found"
        increment_pass
        info "Activating virtual environment..."
        source "$VENV_PATH"
    else
        warning "Virtual environment not found at $VENV_PATH (using system Python)"
        increment_warning
    fi
    
    # Create reports directory
    mkdir -p "$REPORTS_DIR"
    success "Reports directory created: $REPORTS_DIR"
}

# Step 2: Python Version Check
python_version_check() {
    step "Checking Python version..."
    
    increment_check
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
    PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 11 ]; then
        success "Python version $PYTHON_VERSION is supported (3.11+ recommended)"
        increment_pass
    elif [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
        warning "Python version $PYTHON_VERSION detected. Python 3.11+ is recommended."
        warning "Google API Core will stop supporting Python 3.10 after 2026-10-04"
        warning "Consider upgrading to Python 3.11+ for better compatibility"
        increment_warning
    else
        error "Python version $PYTHON_VERSION is too old. Python 3.11+ is required."
        increment_fail
    fi
    
    info "Python executable: $(which python3)"
}

# Step 3: Basic Code Validation
basic_validation() {
    step "Running basic code validation..."
    
    # Check critical files
    local critical_files=(
        "server.py"
        "requirements.txt"
        "Dockerfile"
        "../docker-compose.yaml"
        "alembic.ini"
        "db.py"
    )
    
    for file in "${critical_files[@]}"; do
        increment_check
        local file_path="$PROJECT_ROOT/$file"
        if [ -f "$file_path" ]; then
            success "Found: $file"
            increment_pass
        else
            error "Missing: $file"
            increment_fail
        fi
    done
    
    # Check Python syntax
    increment_check
    info "Checking Python syntax..."
    local syntax_errors=0
    while IFS= read -r file; do
        if ! python3 -m py_compile "$file" 2>/dev/null; then
            syntax_errors=$((syntax_errors + 1))
        fi
    done < <(find . -name "*.py" -type f ! -path "*/__pycache__/*" ! -path "*/alembic/versions/*" ! -path "*/venv/*" ! -path "*/env/*")
    
    if [ $syntax_errors -eq 0 ]; then
        success "Python syntax check passed"
        increment_pass
    else
        error "Found $syntax_errors Python syntax error(s)"
        increment_fail
    fi
}

# Step 3: Install Security & Quality Tools
install_security_tools() {
    step "Installing security and quality tools..."
    
    # Install required packages
    local packages=("bandit" "safety" "flake8" "mypy" "pylint" "black" "isort")
    for package in "${packages[@]}"; do
        install_python_package "$package" || {
            warning "Failed to install $package (non-critical)"
            increment_warning
        }
    done
    
    success "Security tools installation completed"
}

# Step 4: Security Scan (Bandit)
security_scan() {
    step "Running security scan with Bandit..."
    
    increment_check
    info "Running Bandit security scan..."
    if bandit -r . -f json -o "$REPORTS_DIR/bandit-report-$TIMESTAMP.json" \
        --skip B105,B106,B110,B703,B308,B113,B601 \
        --severity-level high \
        --confidence-level high \
        -x "*/__pycache__/*,*/alembic/versions/*,*/venv/*,*/env/*,*/tests/*" 2>/dev/null; then
        success "Bandit security scan passed"
        increment_pass
    else
        warning "Bandit security scan found issues (non-blocking)"
        increment_warning
    fi
    
    # Generate text report
    bandit -r . -f txt \
        --skip B105,B106,B110,B703,B308,B113,B601 \
        --severity-level high \
        --confidence-level high \
        -x "*/__pycache__/*,*/alembic/versions/*,*/venv/*,*/env/*,*/tests/*" \
        > "$REPORTS_DIR/bandit-report-$TIMESTAMP.txt" 2>/dev/null || true
}

# Step 5: Dependency Security Check
dependency_security() {
    step "Running dependency security check..."
    
    increment_check
    info "Checking for security vulnerabilities in dependencies..."
    if safety check --json --output "$REPORTS_DIR/safety-report-$TIMESTAMP.json" 2>/dev/null; then
        success "Dependency security check passed"
        increment_pass
    else
        warning "Dependency security check found issues (non-blocking)"
        increment_warning
    fi
    
    # Generate short report
    safety check --short-report > "$REPORTS_DIR/safety-report-$TIMESTAMP.txt" 2>/dev/null || true
}

# Step 6: Code Quality Check (Flake8)
code_quality() {
    step "Running code quality check with Flake8..."
    
    increment_check
    info "Running Flake8 code quality check..."
    if flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics \
        --exclude="__pycache__,alembic/versions,venv,env,tests" 2>/dev/null; then
        success "Flake8 critical issues check passed"
        increment_pass
    else
        warning "Flake8 found critical issues"
        increment_warning
    fi
    
    # Run comprehensive check
    flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics \
        --exclude="__pycache__,alembic/versions,venv,env,tests" \
        > "$REPORTS_DIR/flake8-report-$TIMESTAMP.txt" 2>/dev/null || true
}

# Step 7: Unused Imports Check
unused_imports_check() {
    step "Checking for unused imports..."
    
    increment_check
    info "Running Flake8 unused imports check (F401)..."
    local unused_count=$(flake8 . --select=F401 --count --statistics \
        --exclude="__pycache__,alembic/versions,venv,env,tests" 2>/dev/null | tail -1 | awk '{print $1}' || echo "0")
    
    if [ "$unused_count" = "0" ] || [ -z "$unused_count" ]; then
        success "No unused imports found"
        increment_pass
    else
        warning "Found $unused_count unused import(s)"
        increment_warning
        flake8 . --select=F401 --show-source --statistics \
            --exclude="__pycache__,alembic/versions,venv,env,tests" \
            > "$REPORTS_DIR/unused-imports-report-$TIMESTAMP.txt" 2>/dev/null || true
    fi
}

# Step 8: Type Checking (mypy)
type_checking() {
    step "Running type checking with mypy..."
    
    increment_check
    if ! command_exists mypy; then
        warning "mypy not installed, skipping type checking"
        increment_warning
        return 0
    fi
    
    info "Running mypy type checking..."
    if mypy . --ignore-missing-imports --no-strict-optional \
        --explicit-package-bases \
        --exclude "(alembic|venv|env|tests|__pycache__)" \
        --show-error-codes > "$REPORTS_DIR/mypy-report-$TIMESTAMP.txt" 2>&1; then
        success "Type checking passed"
        increment_pass
    else
        warning "Type checking found issues (non-blocking)"
        increment_warning
    fi
}

# Step 9: Code Formatting Check (Black)
code_formatting_check() {
    step "Checking code formatting with Black..."
    
    increment_check
    if ! command_exists black; then
        warning "black not installed, skipping formatting check"
        increment_warning
        return 0
    fi
    
    info "Checking code formatting..."
    if black --check --diff . --exclude "(alembic|venv|env|tests|__pycache__)" \
        > "$REPORTS_DIR/black-report-$TIMESTAMP.txt" 2>&1; then
        success "Code formatting is correct"
        increment_pass
    else
        warning "Code formatting issues found - run 'black .' to fix"
        increment_warning
    fi
}

# Step 10: Import Sorting Check (isort)
import_sorting_check() {
    step "Checking import sorting with isort..."
    
    increment_check
    if ! command_exists isort; then
        warning "isort not installed, skipping import sorting check"
        increment_warning
        return 0
    fi
    
    info "Checking import sorting..."
    if isort --check-only --diff . --skip-glob "(alembic/*|venv/*|env/*|tests/*|__pycache__/*)" \
        > "$REPORTS_DIR/isort-report-$TIMESTAMP.txt" 2>&1; then
        success "Import sorting is correct"
        increment_pass
    else
        warning "Import sorting issues found - run 'isort .' to fix"
        increment_warning
    fi
}

# Step 11: Docker Build Test
docker_build_test() {
    step "Testing Docker build..."
    
    increment_check
    if ! command_exists docker; then
        warning "Docker not installed, skipping Docker build test"
        increment_warning
        return 0
    fi
    
    info "Building Docker image..."
    if docker build -t ${PROJECT_NAME,,}-test:$TIMESTAMP . 2>/dev/null; then
        success "Docker build successful"
        increment_pass
        
        # Clean up test image
        docker rmi ${PROJECT_NAME,,}-test:$TIMESTAMP 2>/dev/null || true
    else
        error "Docker build failed"
        increment_fail
    fi
}

# Step 12: Docker Security Scan (Trivy)
docker_security_scan() {
    step "Running Docker security scan..."
    
    increment_check
    if ! command_exists docker; then
        warning "Docker not installed, skipping Docker security scan"
        increment_warning
        return 0
    fi
    
    # Check if Trivy is available
    if ! command_exists trivy; then
        info "Trivy not installed, attempting to run via Docker..."
        if docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
            aquasec/trivy image ${PROJECT_NAME,,}-test:$TIMESTAMP \
            --format json --output "$REPORTS_DIR/trivy-report-$TIMESTAMP.json" 2>/dev/null; then
            success "Docker security scan completed"
            increment_pass
        else
            warning "Docker security scan found issues (non-blocking)"
            increment_warning
        fi
    else
        info "Running Trivy security scan..."
        if trivy image ${PROJECT_NAME,,}-test:$TIMESTAMP \
            --format json --output "$REPORTS_DIR/trivy-report-$TIMESTAMP.json" 2>/dev/null; then
            success "Docker security scan completed"
            increment_pass
        else
            warning "Docker security scan found issues (non-blocking)"
            increment_warning
        fi
    fi
}

# Step 13: Environment Variables Check
env_variables_check() {
    step "Checking environment variables..."
    
    local required_vars=(
        "DATABASE_URL"
        "JWT_SECRET_KEY"
        "API_MODE"
        "MODE"
    )
    
    local recommended_vars=(
        "REDIS_URL"
        "SENTRY_DSN"
        "GOOGLE_STORAGE_BUCKET_NAME"
        "ACCESS_TOKEN_EXPIRY_MINUTES"
        "SESSION_TOKEN_EXPIRY_MINUTES"
        "REFRESH_TOKEN_EXPIRY_MINUTES"
    )
    
    # Check required variables
    for var in "${required_vars[@]}"; do
        increment_check
        if [ -n "${!var}" ]; then
            success "Required environment variable $var is set"
            increment_pass
        else
            error "Required environment variable $var is not set"
            increment_fail
        fi
    done
    
    # Check recommended variables
    for var in "${recommended_vars[@]}"; do
        increment_check
        if [ -n "${!var}" ]; then
            success "Recommended environment variable $var is set"
            increment_pass
        else
            warning "Recommended environment variable $var is not set"
            increment_warning
        fi
    done
    
    # Check for production mode
    increment_check
    if [ "${API_MODE}" = "production" ]; then
        if [ "${DEBUG_MODE:-false}" = "false" ]; then
            success "Production mode configured correctly (DEBUG_MODE=false)"
            increment_pass
        else
            error "DEBUG_MODE should be false in production"
            increment_fail
        fi
    else
        warning "API_MODE is not set to 'production'"
        increment_warning
    fi
}

# Step 14: FastAPI Best Practices Check
fastapi_best_practices() {
    step "Checking FastAPI best practices..."
    
    # Check for proper async usage
    increment_check
    info "Checking for async/await patterns..."
    local async_routes=$(find router -name "*.py" -type f ! -path "*/__pycache__/*" -exec grep -l "async def" {} \; 2>/dev/null | wc -l)
    local sync_routes=$(find router -name "*.py" -type f ! -path "*/__pycache__/*" -exec grep -lE "def [a-z_]+\(.*\):" {} \; 2>/dev/null | wc -l)
    
    if [ "$async_routes" -gt 0 ]; then
        success "Found $async_routes async route handler(s)"
        increment_pass
    fi
    
    if [ "$sync_routes" -gt 0 ] && [ "$async_routes" -eq 0 ]; then
        warning "No async routes found - consider using async for better performance"
        increment_warning
    fi
    
    # Check for Pydantic models
    increment_check
    info "Checking for Pydantic model usage..."
    local pydantic_models=$(find . -name "*.py" -type f ! -path "*/__pycache__/*" ! -path "*/alembic/*" -exec grep -lE "BaseModel|from pydantic" {} \; 2>/dev/null | wc -l)
    if [ "$pydantic_models" -gt 0 ]; then
        success "Found Pydantic models in $pydantic_models file(s)"
        increment_pass
    else
        warning "No Pydantic models found - consider using Pydantic for request/response validation"
        increment_warning
    fi
    
    # Check for dependency injection
    increment_check
    info "Checking for FastAPI dependency injection..."
    local dependencies=$(find router -name "*.py" -type f ! -path "*/__pycache__/*" -exec grep -lE "Depends\(|Annotated\[" {} \; 2>/dev/null | wc -l)
    if [ "$dependencies" -gt 0 ]; then
        success "Found dependency injection in $dependencies file(s)"
        increment_pass
    else
        warning "Limited dependency injection usage - consider using Depends() for better code organization"
        increment_warning
    fi
    
    # Check for proper error handling
    increment_check
    info "Checking for proper error handling..."
    local error_handlers=$(find . -name "*.py" -type f ! -path "*/__pycache__/*" ! -path "*/alembic/*" -exec grep -lE "HTTPException|raise.*Exception" {} \; 2>/dev/null | wc -l)
    if [ "$error_handlers" -gt 0 ]; then
        success "Found error handling in $error_handlers file(s)"
        increment_pass
    else
        warning "Limited error handling found - ensure proper exception handling"
        increment_warning
    fi
    
    # Check for response models
    increment_check
    info "Checking for response model usage..."
    local response_models=$(find router -name "*.py" -type f ! -path "*/__pycache__/*" -exec grep -lE "response_model=" {} \; 2>/dev/null | wc -l)
    if [ "$response_models" -gt 0 ]; then
        success "Found response models in $response_models route(s)"
        increment_pass
    else
        warning "Limited response model usage - consider using response_model for API documentation"
        increment_warning
    fi
}

# Step 15: SQLAlchemy Best Practices Check
sqlalchemy_best_practices() {
    step "Checking SQLAlchemy best practices..."
    
    # Check for connection pooling
    increment_check
    info "Checking for connection pooling configuration..."
    local pool_config=$(find . -name "*.py" -type f ! -path "*/__pycache__/*" ! -path "*/alembic/*" -exec grep -lE "create_engine.*pool|pool_size|max_overflow" {} \; 2>/dev/null | wc -l)
    if [ "$pool_config" -gt 0 ]; then
        success "Found connection pooling configuration"
        increment_pass
    else
        warning "No connection pooling configuration found - configure for better performance"
        increment_warning
    fi
    
    # Check for session management
    increment_check
    info "Checking for proper session management..."
    local session_usage=$(find . -name "*.py" -type f ! -path "*/__pycache__/*" ! -path "*/alembic/*" -exec grep -lE "SessionLocal|sessionmaker|get_db" {} \; 2>/dev/null | wc -l)
    if [ "$session_usage" -gt 0 ]; then
        success "Found session management in $session_usage file(s)"
        increment_pass
    else
        warning "Session management pattern not found"
        increment_warning
    fi
    
    # Check for query optimization
    increment_check
    info "Checking for query optimization patterns..."
    local optimized_queries=$(find . -name "*.py" -type f ! -path "*/__pycache__/*" ! -path "*/alembic/*" -exec grep -lE "joinedload|selectinload|contains_eager" {} \; 2>/dev/null | wc -l)
    if [ "$optimized_queries" -gt 0 ]; then
        success "Found query optimization in $optimized_queries file(s)"
        increment_pass
    else
        info "Consider using joinedload/selectinload for relationship loading"
    fi
}

# Step 16: Alembic Migration Check
alembic_migration_check() {
    step "Checking Alembic migrations..."
    
    increment_check
    if [ ! -f "alembic.ini" ]; then
        error "alembic.ini not found"
        increment_fail
        return 1
    else
        success "alembic.ini found"
        increment_pass
    fi
    
    increment_check
    if [ ! -d "alembic/versions" ]; then
        warning "No migration files found in alembic/versions"
        increment_warning
    else
        local migration_count=$(find alembic/versions -name "*.py" -type f ! -name "__*" 2>/dev/null | wc -l)
        if [ "$migration_count" -gt 0 ]; then
            success "Found $migration_count migration file(s)"
            increment_pass
        else
            warning "No migration files found"
            increment_warning
        fi
    fi
    
    # Check for migration conflicts
    increment_check
    info "Checking for migration conflicts..."
    local duplicate_revs=$(find alembic/versions -name "*.py" -type f -exec grep -h "^revision = " {} \; 2>/dev/null | sort | uniq -d | wc -l)
    if [ "$duplicate_revs" -eq 0 ]; then
        success "No duplicate revision IDs found"
        increment_pass
    else
        error "Found $duplicate_revs duplicate revision ID(s)"
        increment_fail
    fi
}

# Step 17: Logging Validation
logging_validation() {
    step "Validating logging implementation..."
    
    # Check for centralized logger usage
    increment_check
    local logger_imports=$(find . -name "*.py" -type f ! -path "*/__pycache__/*" ! -path "*/alembic/*" -exec grep -lE "from src.logger|from logger import|import logger" {} \; 2>/dev/null | wc -l)
    if [ $logger_imports -gt 0 ]; then
        success "Found $logger_imports files using centralized logger"
        increment_pass
    else
        warning "No files found using centralized logger"
        increment_warning
    fi
    
    # Check for remaining print statements
    increment_check
    local print_statements=$(find . -name "*.py" -type f ! -path "*/__pycache__/*" ! -path "*/alembic/*" ! -path "*/tests/*" -exec grep -cE "print\s*\(" {} \; 2>/dev/null | awk '{sum += $1} END {print sum}')
    if [ "${print_statements:-0}" -eq 0 ]; then
        success "No print statements found - using centralized logging"
        increment_pass
    else
        warning "Found $print_statements print statement(s) - consider using centralized logger"
        increment_warning
    fi
    
    # Check log directory exists
    increment_check
    if [ -d "logs" ]; then
        success "Log directory exists"
        increment_pass
    else
        warning "Log directory not found - will be created at runtime"
        increment_warning
    fi
}

# Step 18: Hardcoded Secrets Check
hardcoded_secrets_check() {
    step "Checking for hardcoded secrets and credentials..."
    
    increment_check
    info "Scanning for potential hardcoded secrets..."
    local secret_patterns=(
        "password\s*=\s*['\"][^'\"]+['\"]"
        "api_key\s*=\s*['\"][^'\"]+['\"]"
        "secret_key\s*=\s*['\"][^'\"]+['\"]"
        "SECRET_KEY\s*=\s*['\"][^'\"]+['\"]"
        "JWT_SECRET\s*=\s*['\"][^'\"]+['\"]"
        "token\s*=\s*['\"][^'\"]+['\"]"
        "aws_secret\s*=\s*['\"][^'\"]+['\"]"
    )
    
    local found_secrets=0
    for pattern in "${secret_patterns[@]}"; do
        local matches=$(find . -name "*.py" -type f ! -path "*/migrations/*" ! -path "*/__pycache__/*" ! -path "*/tests/*" ! -path "*/alembic/*" ! -path "*/venv/*" ! -path "*/env/*" \
            -exec grep -lE "$pattern" {} \; 2>/dev/null | wc -l)
        if [ $matches -gt 0 ]; then
            found_secrets=$((found_secrets + matches))
        fi
    done
    
    if [ $found_secrets -eq 0 ]; then
        success "No obvious hardcoded secrets found"
        increment_pass
    else
        warning "Found potential hardcoded secrets in $found_secrets file(s)"
        increment_warning
        find . -name "*.py" -type f ! -path "*/migrations/*" ! -path "*/__pycache__/*" ! -path "*/tests/*" ! -path "*/alembic/*" ! -path "*/venv/*" ! -path "*/env/*" \
            -exec grep -lE "password\s*=\s*['\"]|api_key\s*=\s*['\"]|secret_key\s*=\s*['\"]" {} \; \
            > "$REPORTS_DIR/potential-secrets-$TIMESTAMP.txt" 2>/dev/null || true
    fi
}

# Step 19: TODO/FIXME Comments Check
todo_fixme_check() {
    step "Checking for TODO/FIXME comments..."
    
    increment_check
    info "Scanning for TODO/FIXME comments..."
    local todo_count=$(find . -name "*.py" -type f ! -path "*/migrations/*" ! -path "*/__pycache__/*" ! -path "*/alembic/*" ! -path "*/venv/*" ! -path "*/env/*" \
        -exec grep -ciE "(TODO|FIXME|XXX|HACK|BUG)" {} \; 2>/dev/null | awk '{sum += $1} END {print sum}')
    
    if [ -z "$todo_count" ] || [ "$todo_count" -eq 0 ]; then
        success "No TODO/FIXME comments found"
        increment_pass
    else
        warning "Found $todo_count TODO/FIXME comment(s) - review before production"
        increment_warning
        find . -name "*.py" -type f ! -path "*/migrations/*" ! -path "*/__pycache__/*" ! -path "*/alembic/*" ! -path "*/venv/*" ! -path "*/env/*" \
            -exec grep -niE "(TODO|FIXME|XXX|HACK|BUG)" {} \; \
            > "$REPORTS_DIR/todo-fixme-report-$TIMESTAMP.txt" 2>/dev/null || true
    fi
}

# Step 20: Requirements File Validation
requirements_check() {
    step "Validating requirements file..."
    
    increment_check
    local requirements_file="$PROJECT_ROOT/requirements.txt"
    
    if [ ! -f "$requirements_file" ]; then
        error "Requirements file not found: $requirements_file"
        increment_fail
        return 1
    fi
    
    success "Requirements file found"
    increment_pass
    
    # Check for pinned versions
    increment_check
    local unpinned=$(grep -E "^[a-zA-Z0-9_\-\.]+$" "$requirements_file" 2>/dev/null | grep -v "^#" | wc -l)
    if [ "$unpinned" -eq 0 ]; then
        success "All dependencies have version pins"
        increment_pass
    else
        warning "Found $unpinned unpinned dependency(ies) - pin versions for production"
        increment_warning
    fi
    
    # Check for security vulnerabilities in requirements
    increment_check
    if safety check --file "$requirements_file" --json > "$REPORTS_DIR/requirements-safety-$TIMESTAMP.json" 2>/dev/null; then
        success "Requirements file security check passed"
        increment_pass
    else
        warning "Requirements file security check found issues"
        increment_warning
    fi
}

# Step 21: CORS Configuration Check
cors_configuration_check() {
    step "Checking CORS configuration..."
    
    increment_check
    info "Checking CORS middleware configuration..."
    local cors_config=$(find . -name "*.py" -type f ! -path "*/__pycache__/*" ! -path "*/alembic/*" -exec grep -lE "CORSMiddleware|allow_origins" {} \; 2>/dev/null | wc -l)
    
    if [ "$cors_config" -gt 0 ]; then
        success "CORS middleware configured"
        increment_pass
        
        # Check for wildcard origins in production
        increment_check
        if grep -rE "allow_origins.*\*" . --include="*.py" ! -path "*/__pycache__/*" ! -path "*/alembic/*" 2>/dev/null | grep -q .; then
            if [ "${API_MODE}" = "production" ]; then
                error "Wildcard CORS origins found in production code"
                increment_fail
            else
                warning "Wildcard CORS origins found - restrict in production"
                increment_warning
            fi
        else
            success "CORS origins are restricted"
            increment_pass
        fi
    else
        warning "CORS middleware not configured"
        increment_warning
    fi
}

# Step 22: Security Middleware Check
security_middleware_check() {
    step "Checking security middleware..."
    
    increment_check
    info "Checking for security middleware..."
    local security_middleware=$(find . -name "*security*.py" -type f ! -path "*/__pycache__/*" ! -path "*/alembic/*" -exec grep -lE "middleware|Middleware" {} \; 2>/dev/null | wc -l)
    
    if [ "$security_middleware" -gt 0 ]; then
        success "Security middleware found"
        increment_pass
    else
        warning "No security middleware found - consider implementing security checks"
        increment_warning
    fi
    
    # Check for input sanitization
    increment_check
    local sanitization=$(find . -name "*.py" -type f ! -path "*/__pycache__/*" ! -path "*/alembic/*" -exec grep -lE "sanitize|escape|clean" {} \; 2>/dev/null | wc -l)
    if [ "$sanitization" -gt 0 ]; then
        success "Input sanitization found"
        increment_pass
    else
        warning "Input sanitization not found - consider implementing"
        increment_warning
    fi
}

# Step 23: Database Query Optimization Check
database_query_optimization() {
    step "Checking database query optimization..."
    
    # Check for N+1 query patterns
    increment_check
    info "Scanning for potential N+1 query patterns..."
    local n1_patterns=$(find . -name "*.py" -type f ! -path "*/migrations/*" ! -path "*/__pycache__/*" ! -path "*/alembic/*" ! -path "*/tests/*" \
        -exec grep -lE "for.*in.*query\(\)|for.*in.*session\.query" {} \; 2>/dev/null | wc -l)
    
    if [ "$n1_patterns" -eq 0 ]; then
        success "No obvious N+1 query patterns found"
        increment_pass
    else
        warning "Found $n1_patterns potential N+1 query pattern(s)"
        increment_warning
        find . -name "*.py" -type f ! -path "*/migrations/*" ! -path "*/__pycache__/*" ! -path "*/alembic/*" ! -path "*/tests/*" \
            -exec grep -lE "for.*in.*query\(\)|for.*in.*session\.query" {} \; \
            > "$REPORTS_DIR/n1-queries-$TIMESTAMP.txt" 2>/dev/null || true
    fi
    
    # Check for eager loading
    increment_check
    local eager_loading=$(find . -name "*.py" -type f ! -path "*/migrations/*" ! -path "*/__pycache__/*" ! -path "*/alembic/*" \
        -exec grep -cE "(joinedload|selectinload|contains_eager)" {} \; 2>/dev/null | awk '{sum += $1} END {print sum}')
    if [ "${eager_loading:-0}" -gt 0 ]; then
        success "Found $eager_loading eager loading pattern(s)"
        increment_pass
    else
        info "Consider using joinedload/selectinload for relationship loading"
    fi
}

# Step 24: Caching Configuration Check
caching_check() {
    step "Checking caching configuration..."
    
    increment_check
    info "Checking for caching implementation..."
    local cache_usage=$(find . -name "*.py" -type f ! -path "*/migrations/*" ! -path "*/__pycache__/*" ! -path "*/alembic/*" \
        -exec grep -cE "(cache\.|@cache|Redis|redis)" {} \; 2>/dev/null | awk '{sum += $1} END {print sum}')
    
    if [ "${cache_usage:-0}" -gt 0 ]; then
        success "Found $cache_usage cache usage instance(s)"
        increment_pass
    else
        warning "Limited cache usage detected - consider implementing caching for better performance"
        increment_warning
    fi
    
    # Check for Redis configuration
    increment_check
    local redis_config=$(find . -name "*.py" -type f ! -path "*/__pycache__/*" ! -path "*/alembic/*" -exec grep -lE "redis|Redis" {} \; 2>/dev/null | wc -l)
    if [ "$redis_config" -gt 0 ]; then
        success "Redis configuration found"
        increment_pass
    else
        info "Consider using Redis for caching and session storage"
    fi
}

# Step 25: API Documentation Check
api_documentation_check() {
    step "Checking API documentation..."
    
    increment_check
    info "Checking for API route documentation..."
    local documented_routes=$(find router -name "*.py" -type f ! -path "*/__pycache__/*" -exec grep -cE "@router\.(get|post|put|delete|patch)" {} \; 2>/dev/null | awk '{sum += $1} END {print sum}')
    local routes_with_docs=$(find router -name "*.py" -type f ! -path "*/__pycache__/*" -exec grep -lE '"""|"""|summary=|description=' {} \; 2>/dev/null | wc -l)
    
    if [ "$documented_routes" -gt 0 ]; then
        if [ "$routes_with_docs" -gt 0 ]; then
            success "Found documentation for routes"
            increment_pass
        else
            warning "Routes found but limited documentation - add docstrings to routes"
            increment_warning
        fi
    else
        info "No routes found to document"
    fi
    
    # Check for OpenAPI tags
    increment_check
    local tagged_routes=$(find router -name "*.py" -type f ! -path "*/__pycache__/*" -exec grep -lE "tags=\[" {} \; 2>/dev/null | wc -l)
    if [ "$tagged_routes" -gt 0 ]; then
        success "Found $tagged_routes route file(s) with tags"
        increment_pass
    else
        warning "Routes not tagged - add tags for better API documentation organization"
        increment_warning
    fi
}

# Step 26: Performance Patterns Check
performance_patterns_check() {
    step "Checking performance patterns..."
    
    # Check for async database operations
    increment_check
    info "Checking for async database operations..."
    local async_db=$(find . -name "*.py" -type f ! -path "*/__pycache__/*" ! -path "*/alembic/*" -exec grep -lE "async.*session|AsyncSession" {} \; 2>/dev/null | wc -l)
    if [ "$async_db" -gt 0 ]; then
        success "Found async database operations"
        increment_pass
    else
        info "Consider using async database operations for better performance"
    fi
    
    # Check for background tasks
    increment_check
    local background_tasks=$(find . -name "*.py" -type f ! -path "*/__pycache__/*" ! -path "*/alembic/*" -exec grep -lE "BackgroundTasks|background" {} \; 2>/dev/null | wc -l)
    if [ "$background_tasks" -gt 0 ]; then
        success "Found background task usage"
        increment_pass
    else
        info "Consider using BackgroundTasks for long-running operations"
    fi
}

# Step 27: Generate Final Report
generate_report() {
    step "Generating final report..."
    
    local report_file="$REPORTS_DIR/production-readiness-report-$TIMESTAMP.txt"
    
    cat > "$report_file" << EOF
FastAPI Backend - Production Readiness Report
Generated: $(date)
Timestamp: $TIMESTAMP

SUMMARY:
========
Total Checks: $TOTAL_CHECKS
Passed: $PASSED_CHECKS
Failed: $FAILED_CHECKS
Warnings: $WARNING_CHECKS

STATUS: $([ $FAILED_CHECKS -eq 0 ] && echo "READY FOR PRODUCTION" || echo "NOT READY FOR PRODUCTION")

DETAILED REPORTS:
================
- Bandit Security Report: bandit-report-$TIMESTAMP.json
- Safety Dependency Report: safety-report-$TIMESTAMP.json
- Flake8 Code Quality Report: flake8-report-$TIMESTAMP.txt
- Unused Imports Report: unused-imports-report-$TIMESTAMP.txt
- Type Checking Report: mypy-report-$TIMESTAMP.txt
- Code Formatting Report: black-report-$TIMESTAMP.txt
- Import Sorting Report: isort-report-$TIMESTAMP.txt
- Trivy Docker Security Report: trivy-report-$TIMESTAMP.json
- Potential Secrets Report: potential-secrets-$TIMESTAMP.txt
- TODO/FIXME Report: todo-fixme-report-$TIMESTAMP.txt
- Requirements Safety: requirements-safety-$TIMESTAMP.json
- N+1 Queries: n1-queries-$TIMESTAMP.txt

RECOMMENDATIONS:
===============
EOF

    if [ $FAILED_CHECKS -gt 0 ]; then
        echo "- Fix all failed checks before production deployment" >> "$report_file"
    fi
    
    if [ $WARNING_CHECKS -gt 0 ]; then
        echo "- Review warnings and address if necessary" >> "$report_file"
    fi
    
    echo "- Review all generated reports for detailed information" >> "$report_file"
    echo "- Test the application thoroughly in staging environment" >> "$report_file"
    echo "- Remove unused imports to improve code quality" >> "$report_file"
    echo "- Address TODO/FIXME comments before production" >> "$report_file"
    echo "- Verify no hardcoded secrets are in the codebase" >> "$report_file"
    echo "- Optimize database queries using eager loading" >> "$report_file"
    echo "- Enable caching for frequently accessed data" >> "$report_file"
    echo "- Configure CORS properly for production" >> "$report_file"
    echo "- Ensure all environment variables are set" >> "$report_file"
    echo "- Run 'black .' to format code" >> "$report_file"
    echo "- Run 'isort .' to sort imports" >> "$report_file"
    echo "- Review security scan reports" >> "$report_file"
    
    success "Final report generated: $report_file"
    info "View all reports in: $REPORTS_DIR"
}

# Main execution
main() {
    print_header
    
    # Run all checks
    setup_environment
    python_version_check
    basic_validation
    install_security_tools
    security_scan
    dependency_security
    code_quality
    unused_imports_check
    type_checking
    code_formatting_check
    import_sorting_check
    docker_build_test
    docker_security_scan
    env_variables_check
    fastapi_best_practices
    sqlalchemy_best_practices
    alembic_migration_check
    logging_validation
    hardcoded_secrets_check
    todo_fixme_check
    requirements_check
    cors_configuration_check
    security_middleware_check
    database_query_optimization
    caching_check
    api_documentation_check
    performance_patterns_check
    generate_report
    
    print_footer
}

# Run main function
main "$@"
