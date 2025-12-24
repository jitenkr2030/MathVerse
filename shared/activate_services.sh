#!/bin/bash

# MathVerse - Service Activation Script
# This script provides convenient commands to activate and work with
# Python virtual environments for all MathVerse services

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Service configurations
SERVICES=(
    "backend:apps/backend/venv"
    "animation-engine:services/animation-engine/venv"
    "video-renderer:services/video-renderer/venv"
    "content-metadata:services/content-metadata/venv"
    "recommendation-engine:services/recommendation-engine/venv"
)

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  MathVerse Virtual Environment Manager${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

show_usage() {
    echo "Usage: ./shared/activate_services.sh <command> [service]"
    echo ""
    echo "Commands:"
    echo "  activate <service>    Activate virtual environment for a service"
    echo "  install <service>     Install dependencies for a service"
    echo "  update <service>      Update dependencies for a service"
    echo "  list                  List all services and their status"
    echo "  help                  Show this help message"
    echo ""
    echo "Available services:"
    for service in "${SERVICES[@]}"; do
        name=$(echo "$service" | cut -d':' -f1)
        echo "  - $name"
    done
}

activate_service() {
    local service_name=$1
    local venv_path=""

    for service in "${SERVICES[@]}"; do
        name=$(echo "$service" | cut -d':' -f1)
        path=$(echo "$service" | cut -d':' -f2)
        if [[ "$name" == "$service_name" ]]; then
            venv_path="$path"
            break
        fi
    done

    if [[ -z "$venv_path" ]]; then
        echo -e "${RED}Error: Service '$service_name' not found${NC}"
        exit 1
    fi

    if [[ ! -d "$venv_path" ]]; then
        echo -e "${RED}Error: Virtual environment not found at $venv_path${NC}"
        echo "Please run './shared/activate_services.sh install $service_name' first"
        exit 1
    fi

    echo -e "${GREEN}Activating $service_name virtual environment...${NC}"
    source "$venv_path/bin/activate"
    echo -e "${GREEN}Virtual environment activated!${NC}"
    echo -e "${YELLOW}To deactivate, run: deactivate${NC}"
    exec bash
}

install_dependencies() {
    local service_name=$1
    local requirements_file=""
    local venv_path=""

    for service in "${SERVICES[@]}"; do
        name=$(echo "$service" | cut -d':' -f1)
        path=$(echo "$service" | cut -d':' -f2)
        if [[ "$name" == "$service_name" ]]; then
            requirements_file="${path%/venv}/requirements.txt"
            venv_path="$path"
            break
        fi
    done

    if [[ -z "$venv_path" ]]; then
        echo -e "${RED}Error: Service '$service_name' not found${NC}"
        exit 1
    fi

    if [[ ! -f "$requirements_file" ]]; then
        echo -e "${RED}Error: Requirements file not found at $requirements_file${NC}"
        exit 1
    fi

    echo -e "${GREEN}Installing dependencies for $service_name...${NC}"
    "$venv_path/bin/pip" install --upgrade pip
    "$venv_path/bin/pip" install -r "$requirements_file"
    echo -e "${GREEN}Dependencies installed successfully!${NC}"
}

update_dependencies() {
    local service_name=$1
    local requirements_file=""
    local venv_path=""

    for service in "${SERVICES[@]}"; do
        name=$(echo "$service" | cut -d':' -f1)
        path=$(echo "$service" | cut -d':' -f2)
        if [[ "$name" == "$service_name" ]]; then
            requirements_file="${path%/venv}/requirements.txt"
            venv_path="$path"
            break
        fi
    done

    if [[ -z "$venv_path" ]]; then
        echo -e "${RED}Error: Service '$service_name' not found${NC}"
        exit 1
    fi

    echo -e "${YELLOW}Updating dependencies for $service_name...${NC}"
    "$venv_path/bin/pip" install --upgrade pip
    "$venv_path/bin/pip" install --upgrade -r "$requirements_file"
    echo -e "${GREEN}Dependencies updated successfully!${NC}"
}

list_services() {
    print_header
    echo "Services Status:"
    echo ""

    for service in "${SERVICES[@]}"; do
        name=$(echo "$service" | cut -d':' -f1)
        path=$(echo "$service" | cut -d':' -f2)

        if [[ -d "$path" ]]; then
            python_version=$("$path/bin/python" --version 2>&1)
            echo -e "${GREEN}✓ $name${NC} ($python_version)"
        else
            echo -e "${RED}✗ $name${NC} (not initialized)"
        fi
    done
}

# Main script logic
case "${1:-help}" in
    activate)
        if [[ -z "${2:-}" ]]; then
            echo -e "${RED}Error: Service name required${NC}"
            show_usage
            exit 1
        fi
        activate_service "$2"
        ;;
    install)
        if [[ -z "${2:-}" ]]; then
            echo -e "${RED}Error: Service name required${NC}"
            show_usage
            exit 1
        fi
        install_dependencies "$2"
        ;;
    update)
        if [[ -z "${2:-}" ]]; then
            echo -e "${RED}Error: Service name required${NC}"
            show_usage
            exit 1
        fi
        update_dependencies "$2"
        ;;
    list)
        list_services
        ;;
    help|--help|-h)
        print_header
        show_usage
        ;;
    *)
        echo -e "${RED}Error: Unknown command '$1'${NC}"
        show_usage
        exit 1
        ;;
esac
