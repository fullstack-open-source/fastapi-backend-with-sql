#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

# Function to prompt with timeout
prompt_with_timeout() {
    local prompt_message=$1
    local default_choice=$2
    local timeout=$3
    local user_input

    read -t "$timeout" -p "$prompt_message" user_input || user_input="$default_choice"
    echo "$user_input"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to wait for service health
wait_for_health() {
    local service=$1
    local max_attempts=${2:-30}
    local attempt=0
    
    print_info "Waiting for $service to be healthy..."
    while [ $attempt -lt $max_attempts ]; do
        if docker compose ps "$service" | grep -q "healthy"; then
            print_success "$service is healthy"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    
    print_warning "$service did not become healthy within timeout"
    return 1
}

# Function to check service status
check_service_status() {
    local service=$1
    local status=$(docker compose ps "$service" --format json 2>/dev/null | grep -o '"State":"[^"]*"' | cut -d'"' -f4 || echo "unknown")
    echo "$status"
}

echo "--------------------------------------------------"
echo "🚀 DOCKER COMPOSE RELOAD SCRIPT"
echo "--------------------------------------------------"

# Check if docker compose is available
if ! command_exists docker; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
    print_error "Docker Compose is not available"
    exit 1
fi

# Check if docker-compose.yaml exists
if [ ! -f "docker-compose.yaml" ]; then
    print_error "docker-compose.yaml not found in current directory"
    exit 1
fi

# Ask for no-cache build
choice=$(prompt_with_timeout "Do you want to build with --no-cache? (y/N) [auto-skip in 5s]: " "n" 5)
if [[ "$choice" =~ ^[Yy]([Ee][Ss])?$ ]]; then
    print_info "Running docker compose build --no-cache..."
    if docker compose build --no-cache; then
        print_success "Build completed successfully"
    else
        print_error "Build failed"
        exit 1
    fi
else
    print_info "Skipping no-cache build..."
fi

# Ask to push to Docker Hub (only if build was selected)
if [[ "$choice" =~ ^[Yy]([Ee][Ss])?$ ]]; then
    push_choice=$(prompt_with_timeout "Do you want to push the image to Docker Hub? (y/N) [auto-skip in 5s]: " "n" 5)
    if [[ "$push_choice" =~ ^[Yy]([Ee][Ss])?$ ]]; then
        print_info "Pushing Docker images to Docker Hub..."
        if docker compose push; then
            print_success "Images pushed successfully"
        else
            print_error "Failed to push images"
            exit 1
        fi
    else
        print_info "Skipping Docker Hub push..."
    fi
fi

# Check and create Docker network if it doesn't exist
NETWORK_NAME="fastapi_backend_with_postgresql_network"
print_info "Checking Docker network: $NETWORK_NAME..."
if ! docker network inspect "$NETWORK_NAME" >/dev/null 2>&1; then
    print_info "Creating Docker network: $NETWORK_NAME..."
    if docker network create --driver bridge "$NETWORK_NAME"; then
        print_success "Network created successfully"
    else
        print_error "Failed to create network"
        exit 1
    fi
else
    print_success "Network already exists"
fi

# Bring down existing containers
print_info "Bringing down Docker containers..."
if docker compose down; then
    print_success "Containers stopped and removed"
else
    print_warning "Some containers may not have been stopped properly"
fi

# Start containers
print_info "Starting Docker containers in detached mode..."
if docker compose up -d; then
    print_success "Containers started"
else
    print_error "Failed to start containers"
    exit 1
fi

# Wait for critical services to be healthy
print_info "Waiting for services to be ready..."
wait_for_health "db" 30
wait_for_health "redis" 30
wait_for_health "api" 60

# Show service status
echo ""
echo "--------------------------------------------------"
echo "📊 SERVICE STATUS"
echo "--------------------------------------------------"
docker compose ps

# Ask if user wants to follow logs
log_choice=$(prompt_with_timeout "Do you want to follow logs? (y/N) [auto-skip in 5s]: " "n" 5)
if [[ "$log_choice" =~ ^[Yy]([Ee][Ss])?$ ]]; then
    service_choice=$(prompt_with_timeout "Which service logs? (api/nginx/db/redis/pgadmin/all) [default: api]: " "api" 5)
    if [ "$service_choice" = "all" ]; then
        print_info "Following all service logs (Ctrl+C to exit)..."
        docker compose logs -f
    else
        print_info "Following $service_choice logs (Ctrl+C to exit)..."
        docker compose logs -f "$service_choice"
    fi
else
    print_info "Skipping log following..."
    echo ""
    print_success "Deployment completed successfully!"
    echo ""
    echo "Access your services:"
    echo "  - API: http://localhost:8000"    # API_DEBUG_PORT
    echo "  - Nginx: http://localhost:8001"    # PROXY_PORT
    echo "  - pgAdmin: http://localhost:5050"    # PGADMIN_PORT
    echo ""
    echo "Available services: api, nginx, db, redis, pgadmin"
    echo "To view logs later, run: docker compose logs -f [service]"
fi




echo "--------------------------------------------------"
echo "✅ RELOAD SCRIPT FINISHED"
echo "--------------------------------------------------"

