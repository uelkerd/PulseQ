*** Settings ***
Documentation     Basic load balancer testing scenarios
Library           LoadBalancerKeywords
Suite Setup       Initialize Load Balancer
Suite Teardown    Generate Performance Report

*** Variables ***
${NODE1_ID}      node1
${NODE2_ID}      node2
${NODE3_ID}      node3
${DURATION}      60
${THRESHOLD}     0.8

*** Test Cases ***
Test Basic Load Balancing
    [Documentation]    Test basic load balancing functionality
    Add Node    ${NODE1_ID}    {"cpu": 4, "memory": 8, "network": 1000}
    Add Node    ${NODE2_ID}    {"cpu": 4, "memory": 8, "network": 1000}
    Add Node    ${NODE3_ID}    {"cpu": 4, "memory": 8, "network": 1000}
    
    Run Workload Pattern    basic    ${DURATION}
    
    ${metrics}    Get Metrics
    Verify Load Balance    ${THRESHOLD}
    Verify Success Rate    ${THRESHOLD}

Test Resource Monitoring
    [Documentation]    Test resource monitoring capabilities
    Update Node Load    ${NODE1_ID}    {"cpu_usage": 0.7, "memory_usage": 0.6}
    Update Node Load    ${NODE2_ID}    {"cpu_usage": 0.5, "memory_usage": 0.4}
    Update Node Load    ${NODE3_ID}    {"cpu_usage": 0.3, "memory_usage": 0.2}
    
    Run Workload Pattern    resource_monitoring    ${DURATION}
    
    ${metrics}    Get Metrics
    Verify Load Balance    ${THRESHOLD}
    Verify Success Rate    ${THRESHOLD}

Test Node Removal
    [Documentation]    Test load balancer behavior when removing nodes
    Remove Node    ${NODE3_ID}
    
    Run Workload Pattern    node_removal    ${DURATION}
    
    ${metrics}    Get Metrics
    Verify Load Balance    ${THRESHOLD}
    Verify Success Rate    ${THRESHOLD}

Test Edge Cases
    [Documentation]    Test load balancer behavior under edge cases
    Run Edge Case Test    cpu_saturation    ${DURATION}
    Run Edge Case Test    memory_pressure    ${DURATION}
    Run Edge Case Test    network_congestion    ${DURATION}
    
    ${metrics}    Get Metrics
    Verify Load Balance    ${THRESHOLD}
    Verify Success Rate    ${THRESHOLD}

Test Workload Transitions
    [Documentation]    Test load balancer behavior during workload transitions
    Run Transition Test    ecommerce    streaming    ${DURATION}
    Run Transition Test    streaming    iot    ${DURATION}
    Run Transition Test    iot    mixed    ${DURATION}
    
    ${metrics}    Get Metrics
    Verify Load Balance    ${THRESHOLD}
    Verify Success Rate    ${THRESHOLD}

*** Keywords ***
Initialize Load Balancer
    Initialize Load Balancer    config_file=${CURDIR}/config.json

Generate Performance Report
    Generate Performance Report    output_dir=${CURDIR}/reports 