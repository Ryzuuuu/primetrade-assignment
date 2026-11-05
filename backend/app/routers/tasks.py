from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])


def _get_task_or_error(task_id: int, db: Session, current_user) -> models.Task:
    """Fetch a task, enforcing that the caller owns it (or is an admin)."""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return task


@router.post("/", response_model=schemas.TaskResponse, status_code=201)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    new_task = models.Task(**task.model_dump(), owner_id=current_user.id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@router.get("/", response_model=List[schemas.TaskResponse])
def get_tasks(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Admin sees all tasks, user sees only their own
    query = db.query(models.Task)
    if current_user.role != "admin":
        query = query.filter(models.Task.owner_id == current_user.id)
    return query.order_by(models.Task.id).all()


@router.put("/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    task = _get_task_or_error(task_id, db, current_user)
    for key, value in task_update.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    task = _get_task_or_error(task_id, db, current_user)
    db.delete(task)
    db.commit()


@router.get("/admin/all", response_model=List[schemas.TaskResponse])
def admin_all_tasks(db: Session = Depends(get_db), _=Depends(require_admin)):
    return db.query(models.Task).order_by(models.Task.id).all()
