"""Configuration endpoints for SQL dialects and system settings."""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

router = APIRouter(prefix="/api/v1/config", tags=["config"])


@router.get("/sql-dialects")
async def get_sql_dialects() -> Dict[str, Any]:
    """Get available SQL dialects for SQL ingestion.
    
    Returns list of supported SQL dialects with their configurations.
    Frontend uses this to populate dialect selector during ingestion.
    
    Returns:
        Dictionary with 'dialects' list and 'default' dialect ID
    """
    try:
        from ...config.sql_dialects import get_enabled_dialects, get_default_dialect
        
        enabled = get_enabled_dialects()
        default = get_default_dialect()
        
        return {
            "dialects": enabled,
            "default": default["id"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch SQL dialects: {e}"
        )
