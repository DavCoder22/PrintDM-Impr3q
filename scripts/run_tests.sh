#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Install dependencies from the root directory
echo -e "\n${GREEN}Installing dependencies...${NC}"
pip install -r ../requirements.txt

# Function to run tests for a service
run_service_tests() {
    local service_name=$1
    local service_path="../services/$service_name"
    
    echo -e "\n${GREEN}Running tests for $service_name...${NC}"
    
    if [ ! -d "$service_path" ]; then
        echo -e "${RED}Error: Directory $service_path does not exist${NC}"
        return 1
    fi
    
    cd "$service_path" || return 1
    
    # Run tests with coverage
    echo "Running tests..."
    if ! pytest -v --cov=app tests/; then
        echo -e "${RED}Tests failed for $service_name${NC}"
        cd - > /dev/null || return 1
        return 1
    fi
    
    echo -e "${GREEN}All tests passed for $service_name${NC}"
    cd - > /dev/null || return 1
    return 0
}

# Main execution
echo "Starting test suite..."

# Run tests for each service
SERVICES=("printers-service" "calibration-service" "monitoring-service")

for service in "${SERVICES[@]}"; do
    if ! run_service_tests "$service"; then
        echo -e "${RED}Test suite failed in $service${NC}"
        exit 1
    fi
done

echo -e "\n${GREEN}All tests passed successfully!${NC}"
exit 0
