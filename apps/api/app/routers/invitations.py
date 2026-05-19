from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import require_principal_id
from app.schemas.invitation import InvitationCreate, InvitationResponse
from app.services.invitations_service import InvitationsService

router = APIRouter(prefix="/teams/{team_id}/invitations", tags=["invitations"])


def get_invitations_service(db: Session = Depends(get_db)) -> InvitationsService:
    return InvitationsService(db)


@router.post("", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
def create_invitation(
    team_id: int,
    invitation_data: InvitationCreate,
    service: InvitationsService = Depends(get_invitations_service),
    principal_id: str = Depends(require_principal_id),
) -> InvitationResponse:
    try:
        invitation = service.create_invitation(
            team_id=team_id,
            acting_principal_id=principal_id,
            email=invitation_data.email,
            role=invitation_data.role,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    if invitation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    return InvitationResponse.model_validate(invitation)


@router.delete("/{invitation_id}", response_model=InvitationResponse)
def revoke_invitation(
    team_id: int,
    invitation_id: int,
    service: InvitationsService = Depends(get_invitations_service),
    principal_id: str = Depends(require_principal_id),
) -> InvitationResponse:
    try:
        invitation = service.revoke_invitation(
            team_id=team_id,
            invitation_id=invitation_id,
            acting_principal_id=principal_id,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    if invitation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")

    return InvitationResponse.model_validate(invitation)
