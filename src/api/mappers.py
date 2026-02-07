from src.api.schemas import AdmissionRequest
from src.modules.admission.dto import AdmitLLMRequestUseCaseInputDTO


def map_request_to_use_case_dto(request: AdmissionRequest) -> AdmitLLMRequestUseCaseInputDTO:
    return AdmitLLMRequestUseCaseInputDTO(
        pipeline=request.pipeline,
        priority=request.priority,
        estimated_tokens=request.estimated_tokens,
        request_id=request.request_id,
    )
