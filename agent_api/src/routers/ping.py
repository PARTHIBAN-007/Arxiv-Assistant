from fastapi import APIRouter
from sqlalchemy import text

from ..dependencies import DatabaseDep, OpenSearchDep, SettingsDep
from ..schemas.api.health import HealthResponse, ServiceStatus
from ..services.ollama import OllamaClient

router = APIRouter()

@router.get("/ping",tags = ["Health"])
async def ping():
    """Endpoint for Health Check"""
    return {"status":"ok","message":"Ping"}


@router.get("/health",response_model=HealthResponse,tags = ["Health"])
async def health_check(
    settings:SettingsDep,
    database:DatabaseDep,
    opensearch_client:OpenSearchDep
) -> HealthResponse:
    """Health checkpoint for monitoring and load balance"""

    services = {}
    overall_status = "ok"

    def _check_service(name:str,check_func,*args,**kwargs):
        """Helper to standardize service health check"""
        pass

    def _check_database():
        with database.get_session() as session:
            session.execute(text("SELECT 1"))
        return ServiceStatus(status="healthy",message = "Connected Successfully")

    def _check_opensearch():
        if not opensearch_client.health_check():
            return ServiceStatus(status= "unhealth",message = "Not Responding")
        stats = opensearch_client.get_index_stats()
        return ServiceStatus(
            status= "healthy",
            description = f"Index {stats.get('index_name','unknown')} with {stats.get('document_count',0)} documents"
        )
    
    _check_service("database",_check_database)
    _check_service("opensearch",_check_opensearch)

    try:
        ollama_client = OllamaClient(settings)
        ollama_health = await ollama_client.health_check()
        services["ollama"] = ServiceStatus(status = ollama_health["status"],message = ollama_health["message"])
        if ollama_health["status"] != "healthy":
            overall_status ="degraded"
    except Exception as e:
        services["ollama"] = ServiceStatus(status = "unhealthy",message = str(e))
        overall_status = "degraded"
    
    return HealthResponse(
        status = overall_status,
        version = settings.app_version,
        environment = settings.environment,
        service_name = settings.service_name ,
        services = services
    )