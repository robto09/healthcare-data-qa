"""
Healthcare Data QA Automation - API Tests

This module provides tests for:
1. Data ingestion endpoints
2. Quality check endpoints
3. Validation result endpoints
4. Model validation endpoints

Author: Robert Torres
"""

import pytest
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

class TestAPIEndpoints:
    """Test suite for API endpoint validation."""
    
    def test_health_check(self, api_client):
        """Test API health check endpoint."""
        response = api_client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_data_ingestion(self, api_client, test_data):
        """Test data ingestion endpoint."""
        # Convert test data to JSON
        data_json = test_data.to_json(orient="records")
        
        # Test data upload
        response = api_client.post(
            "/data/upload",
            json_data={"data": data_json}
        )
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        assert result["records_processed"] == len(test_data)
        
        # Verify uploaded data
        response = api_client.get("/data/latest")
        assert response.status_code == 200
        
        loaded_data = pd.DataFrame(response.json()["data"])
        pd.testing.assert_frame_equal(loaded_data, test_data)
    
    def test_quality_check_trigger(self, api_client):
        """Test quality check trigger endpoint."""
        response = api_client.post(
            "/quality/check",
            json_data={
                "checks": ["schema", "completeness", "uniqueness", "outliers"]
            }
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "job_id" in result
        assert "timestamp" in result
        
        # Get quality check results
        job_id = result["job_id"]
        response = api_client.get(f"/quality/results/{job_id}")
        assert response.status_code == 200
        
        check_results = response.json()
        assert "schema_check" in check_results
        assert "completeness_check" in check_results
        assert "uniqueness_check" in check_results
        assert "outlier_check" in check_results
    
    def test_validation_history(self, api_client):
        """Test validation history endpoint."""
        response = api_client.get("/quality/history")
        assert response.status_code == 200
        
        history = response.json()
        assert isinstance(history, list)
        
        if len(history) > 0:
            entry = history[0]
            assert "job_id" in entry
            assert "timestamp" in entry
            assert "status" in entry
            assert "checks_performed" in entry
    
    def test_model_validation(self, api_client):
        """Test model validation endpoint."""
        validation_request = {
            "model_name": "healthcare_cost_predictor",
            "model_version": "1.0.0",
            "validation_type": "full",
            "metrics": {
                "mse": 21073365.42,
                "rmse": 4590.57,
                "mae": 2533.67,
                "r2": 0.86
            },
            "bias_analysis": {
                "age_disparity": 8.62,
                "sex_disparity": 1.16
            }
        }
        
        response = api_client.post(
            "/model/validate",
            json_data=validation_request
        )
        assert response.status_code == 200
        
        result = response.json()
        assert result["validation_passed"] is True
        assert "validation_id" in result
        assert "timestamp" in result
        
        # Get validation details
        validation_id = result["validation_id"]
        response = api_client.get(f"/model/validation/{validation_id}")
        assert response.status_code == 200
        
        validation_details = response.json()
        assert validation_details["model_name"] == validation_request["model_name"]
        assert validation_details["model_version"] == validation_request["model_version"]
        assert "metrics" in validation_details
        assert "bias_analysis" in validation_details
    
    def test_metrics_summary(self, api_client):
        """Test metrics summary endpoint."""
        response = api_client.get("/quality/metrics/summary")
        assert response.status_code == 200
        
        summary = response.json()
        assert "latest_validation" in summary
        assert "historical_trend" in summary
        assert "compliance_status" in summary
    
    def test_error_handling(self, api_client):
        """Test API error handling."""
        # Test invalid endpoint
        response = api_client.get("/invalid/endpoint")
        assert response.status_code == 404
        
        # Test invalid data upload
        response = api_client.post(
            "/data/upload",
            json_data={"data": "invalid_json"}
        )
        assert response.status_code == 400
        
        error = response.json()
        assert "error" in error
        assert "message" in error
        
        # Test invalid job ID
        response = api_client.get("/quality/results/invalid_job_id")
        assert response.status_code == 404
        
        # Test missing required parameters
        response = api_client.post("/quality/check", json_data={})
        assert response.status_code == 400
        
        error = response.json()
        assert "error" in error
        assert "message" in error
    
    def test_large_data_handling(self, api_client, test_data):
        """Test handling of large data uploads."""
        # Create large dataset
        large_data = pd.concat([test_data] * 1000, ignore_index=True)
        data_json = large_data.to_json(orient="records")
        
        # Test chunked upload
        chunk_size = 1000
        total_chunks = len(large_data) // chunk_size + 1
        
        for i in range(total_chunks):
            start_idx = i * chunk_size
            end_idx = min((i + 1) * chunk_size, len(large_data))
            chunk = large_data.iloc[start_idx:end_idx]
            
            response = api_client.post(
                "/data/upload/chunk",
                json_data={
                    "data": chunk.to_json(orient="records"),
                    "chunk_number": i + 1,
                    "total_chunks": total_chunks
                }
            )
            assert response.status_code == 200
            
            result = response.json()
            assert result["success"] is True
            assert "chunk_processed" in result
        
        # Verify complete upload
        response = api_client.get("/data/count")
        assert response.status_code == 200
        
        count = response.json()["count"]
        assert count == len(large_data)