import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request, Response, status

from src.api.schemas import AdmissionDecision, AdmissionRequest, AdmissionResponse
from src.bootstrap.containers import Container
from src.modules.admission.dto import AdmitLLMRequestUseCaseInputDTO
from src.modules.admission.use_case import AdmitLLMRequestUseCase
from src.modules.commons import Priority, SourcePipeline
from src.modules.policy.exceptions import InvalidPipelineError

router = APIRouter()

_LOGGER = logging.getLogger()


@router.post("/v1/evaluate", response_model=AdmissionResponse, response_model_exclude_none=True)
@inject
async def evaluate(
    request: AdmissionRequest,
    use_case: AdmitLLMRequestUseCase = Depends(Provide[Container.process_request]),
) -> AdmissionResponse | Response:
    dto = _map_request_to_use_case_dto(request)
    try:
        admission_response = await use_case.execute(dto)
        return AdmissionResponse(decision=AdmissionDecision(admission_response.decision))
    except InvalidPipelineError as e:
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))
    except Exception as e:
        _LOGGER.error(f"Service Failure: {e}", exc_info=True)
        return AdmissionResponse(decision=AdmissionDecision.ALLOW)  # Fail open


def _map_request_to_use_case_dto(request: AdmissionRequest) -> AdmitLLMRequestUseCaseInputDTO:
    return AdmitLLMRequestUseCaseInputDTO(
        pipeline=SourcePipeline(request.pipeline),
        priority=Priority(request.priority),
        estimated_tokens=request.estimated_tokens,
        request_id=request.request_id,
    )


@router.post("/health")
async def healthcheck(request: Request) -> Response:
    return Response(status_code=status.HTTP_200_OK)
