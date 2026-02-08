from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.api.schemas import AdmissionRequest, AdmissionResponse
from src.bootstrap.containers import Container
from src.modules.admission.dto import AdmitLLMRequestUseCaseInputDTO
from src.modules.admission.use_case import AdmitLLMRequestUseCase

router = APIRouter()


@router.post("/v1/evaluate", response_model=AdmissionResponse)
@inject
async def evaluate(
    request: AdmissionRequest,
    use_case: AdmitLLMRequestUseCase = Depends(Provide[Container.process_request]),
) -> AdmissionResponse:
    dto = _map_request_to_use_case_dto(request)
    admission_response = use_case.execute(dto)
    return AdmissionResponse(decision=admission_response.decision)


def _map_request_to_use_case_dto(request: AdmissionRequest) -> AdmitLLMRequestUseCaseInputDTO:
    return AdmitLLMRequestUseCaseInputDTO(
        pipeline=request.pipeline,
        priority=request.priority,
        estimated_tokens=request.estimated_tokens,
        request_id=request.request_id,
    )
