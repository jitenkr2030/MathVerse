from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.schemas.content_schema import (
    SyllabusNodeCreate,
    SyllabusNodeUpdate,
    SyllabusNodeResponse,
    SyllabusTreeResponse,
)
from app.models.course import Syllabus


router = APIRouter()


@router.get("/", response_model=List[SyllabusNodeResponse])
async def get_syllabus_nodes(
    parent_id: Optional[int] = Query(default=None, description="Filter by parent ID"),
    node_type: Optional[str] = Query(default=None, description="Filter by node type"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get syllabus nodes, optionally filtered by parent or type.
    """
    query = select(Syllabus)
    
    if parent_id is not None:
        query = query.where(Syllabus.parent_id == parent_id)
    if node_type:
        query = query.where(Syllabus.node_type == node_type)
    
    query = query.order_by(Syllabus.order_index)
    
    result = await db.execute(query)
    nodes = result.scalars().all()
    
    return nodes


@router.get("/{node_id}", response_model=SyllabusNodeResponse)
async def get_syllabus_node(
    node_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific syllabus node.
    """
    result = await db.execute(
        select(Syllabus).where(Syllabus.id == node_id)
    )
    node = result.scalar_one_or_none()
    
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Syllabus node {node_id} not found"
        )
    
    return node


@router.post("/", response_model=SyllabusNodeResponse, status_code=status.HTTP_201_CREATED)
async def create_syllabus_node(
    node: SyllabusNodeCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new syllabus node.
    """
    # Build path and depth for hierarchical structure
    if node.parent_id:
        parent_result = await db.execute(
            select(Syllabus).where(Syllabus.id == node.parent_id)
        )
        parent = parent_result.scalar_one_or_none()
        
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Parent node {node.parent_id} not found"
            )
        
        path = f"{parent.path}/{node.name}" if parent.path else node.name
        depth = parent.depth + 1
    else:
        path = node.name
        depth = 0
    
    db_node = Syllabus(
        **node.model_dump(),
        path=path,
        depth=depth
    )
    
    db.add(db_node)
    
    try:
        await db.commit()
        await db.refresh(db_node)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create syllabus node: {str(e)}"
        )
    
    return db_node


@router.patch("/{node_id}", response_model=SyllabusNodeResponse)
async def update_syllabus_node(
    node_id: int,
    update: SyllabusNodeUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a syllabus node.
    """
    result = await db.execute(
        select(Syllabus).where(Syllabus.id == node_id)
    )
    db_node = result.scalar_one_or_none()
    
    if not db_node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Syllabus node {node_id} not found"
        )
    
    # Update fields
    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_node, field, value)
    
    # If name changed, update path for this node and all children
    if "name" in update_data and db_node.parent_id:
        parent_result = await db.execute(
            select(Syllabus).where(Syllabus.id == db_node.parent_id)
        )
        parent = parent_result.scalar_one_or_none()
        if parent:
            new_path = f"{parent.path}/{db_node.name}" if parent.path else db_node.name
            db_node.path = new_path
    
    try:
        await db.commit()
        await db.refresh(db_node)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update syllabus node: {str(e)}"
        )
    
    return db_node


@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_syllabus_node(
    node_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a syllabus node.
    Children will be reassigned to the deleted node's parent.
    """
    result = await db.execute(
        select(Syllabus).where(Syllabus.id == node_id)
    )
    db_node = result.scalar_one_or_none()
    
    if not db_node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Syllabus node {node_id} not found"
        )
    
    try:
        # Reassign children to parent
        if db_node.parent_id:
            await db.execute(
                Syllabus.__table__.update()
                .where(Syllabus.parent_id == node_id)
                .values(parent_id=db_node.parent_id)
            )
        
        await db.delete(db_node)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete syllabus node: {str(e)}"
        )
