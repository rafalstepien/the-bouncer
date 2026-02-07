from src.api.schemas import AdmissionRequest, AdmissionResponse, AdmissionDecision
from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from src.bootstrap.containers import Container
from src.modules.bouncer.application.use_cases.process_request import ProcessRequest


router = APIRouter()


@router.post("/v1/evaluate", response_model=AdmissionResponse)
@inject
def evaluate(
    request: AdmissionRequest,
    use_case: ProcessRequest = Depends(Provide[Container.process_request]),
) -> AdmissionResponse:
    uc_response = use_case.execute(request)
    return AdmissionResponse(decision=AdmissionDecision.ALLOW)
