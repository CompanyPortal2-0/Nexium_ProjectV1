# Diagnostic Script - Check why pods are crashing

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Diagnostic Information" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Checking auth-service logs..." -ForegroundColor Yellow
kubectl logs -l app=auth-service --tail=50
Write-Host ""

Write-Host "Checking user-service logs..." -ForegroundColor Yellow
kubectl logs -l app=user-service --tail=50
Write-Host ""

Write-Host "Checking gateway logs..." -ForegroundColor Yellow
kubectl logs -l app=gateway --tail=50
Write-Host ""

Write-Host "Describing auth-service pod..." -ForegroundColor Yellow
kubectl describe pod -l app=auth-service
Write-Host ""