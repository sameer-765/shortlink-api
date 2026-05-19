from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import require_principal_id
from app.schemas.comment import CommentCreate, CommentResponse
from app.services.comments_service import CommentsService

router = APIRouter(prefix="/teams/{team_id}/links/{link_id}/comments", tags=["comments"])


def get_comments_service(db: Session = Depends(get_db)) -> CommentsService:
    return CommentsService(db)


@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    team_id: int,
    link_id: int,
    comment_data: CommentCreate,
    service: CommentsService = Depends(get_comments_service),
    principal_id: str = Depends(require_principal_id),
) -> CommentResponse:
    try:
        comment = service.create_comment(
            team_id=team_id,
            link_id=link_id,
            acting_principal_id=principal_id,
            body=comment_data.body,
            parent_id=comment_data.parent_id,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    return CommentResponse.model_validate(comment)


@router.get("", response_model=list[CommentResponse])
def list_comments(
    team_id: int,
    link_id: int,
    service: CommentsService = Depends(get_comments_service),
    principal_id: str = Depends(require_principal_id),
) -> list[CommentResponse]:
    try:
        comments = service.list_comments(
            team_id=team_id,
            link_id=link_id,
            acting_principal_id=principal_id,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    if comments is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    return [CommentResponse.model_validate(comment) for comment in comments]


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    team_id: int,
    link_id: int,
    comment_id: int,
    service: CommentsService = Depends(get_comments_service),
    principal_id: str = Depends(require_principal_id),
) -> None:
    try:
        deleted = service.delete_comment(
            team_id=team_id,
            link_id=link_id,
            comment_id=comment_id,
            acting_principal_id=principal_id,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    if deleted is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
