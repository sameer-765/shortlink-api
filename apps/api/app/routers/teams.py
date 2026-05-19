from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import require_principal_id
from app.schemas.team import TeamCreate, TeamMemberCreate, TeamMemberResponse, TeamResponse
from app.services.teams_service import InvalidTeamMemberRoleError, TeamsService

router = APIRouter(prefix="/teams", tags=["teams"])


def get_teams_service(db: Session = Depends(get_db)) -> TeamsService:
    return TeamsService(db)


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(
    team_data: TeamCreate,
    service: TeamsService = Depends(get_teams_service),
    principal_id: str = Depends(require_principal_id),
) -> TeamResponse:
    team = service.create_team(name=team_data.name, owner_principal_id=principal_id)
    return TeamResponse.model_validate(team)


@router.post("/{team_id}/members", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
def add_team_member(
    team_id: int,
    member_data: TeamMemberCreate,
    service: TeamsService = Depends(get_teams_service),
    principal_id: str = Depends(require_principal_id),
) -> TeamMemberResponse:
    try:
        member = service.add_team_member(
            team_id=team_id,
            acting_principal_id=principal_id,
            principal_id=member_data.principal_id,
            role=member_data.role,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except InvalidTeamMemberRoleError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    return TeamMemberResponse.model_validate(member)
