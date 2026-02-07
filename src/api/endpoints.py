from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.api.mappers import map_request_to_use_case_dto
from src.api.schemas import AdmissionRequest, AdmissionResponse
from src.bootstrap.containers import Container
from src.modules.admission.use_case import AdmitLLMRequestUseCase

router = APIRouter()


@router.post("/v1/evaluate", response_model=AdmissionResponse)
@inject
def evaluate(
    request: AdmissionRequest,
    use_case: AdmitLLMRequestUseCase = Depends(Provide[Container.process_request]),
) -> AdmissionResponse:
    dto = map_request_to_use_case_dto(request)
    admit_response = use_case.execute(dto)
    return AdmissionResponse(decision=admit_response.decision)
