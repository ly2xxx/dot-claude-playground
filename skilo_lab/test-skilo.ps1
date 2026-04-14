#!/usr/bin/env pwsh

# Test Skilo functionality on various skill examples

Write-Host "=== Skilo Lab Tests ===" -ForegroundColor Cyan

# Check if skilo is installed
try {
    $skiloVersion = & skilo --version
    Write-Host "✓ Skilo installed: $skiloVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Skilo not found. Install with: cargo install skilo" -ForegroundColor Red
    exit 1
}

Write-Host "`n--- Testing Skills ---" -ForegroundColor Yellow

# Test good skill
Write-Host "`nTesting good-skill..." -ForegroundColor Blue
& skilo validate good-skill/
& skilo fmt --check good-skill/SKILL.md

# Test bad skill (should show errors)
Write-Host "`nTesting bad-skill (expecting errors)..." -ForegroundColor Blue
& skilo validate bad-skill/
& skilo fmt --check bad-skill/SKILL.md

# Test complex skill
Write-Host "`nTesting complex-skill..." -ForegroundColor Blue
& skilo validate complex-skill/
& skilo fmt --check complex-skill/SKILL.md

# Format all skills
Write-Host "`n--- Formatting All Skills ---" -ForegroundColor Yellow
& skilo fmt .

# Summary
Write-Host "`n=== Test Complete ===" -ForegroundColor Cyan
Write-Host "Review the output above to see validation results and formatting changes."