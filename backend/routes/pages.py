"""Page API routes."""
from fastapi import APIRouter, HTTPException, Depends
from models.page import PageCreate, PageUpdate, PageResponse
from services import page_service
from middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/pages", tags=["Pages"])


@router.get("", response_model=list[PageResponse])
def get_pages(current_user: dict = Depends(get_current_user)):
    """Get all pages: created by user OR shared with user."""
    pages = page_service.get_all_pages(current_user["id"])
    return pages


@router.get("/my", response_model=list[PageResponse])
def get_my_pages(current_user: dict = Depends(get_current_user)):
    """Get pages created by the current user."""
    pages = page_service.get_my_pages(current_user["id"])
    return pages


@router.get("/shared", response_model=list[PageResponse])
def get_shared_pages(current_user: dict = Depends(get_current_user)):
    """Get pages shared with the current user."""
    pages = page_service.get_shared_pages(current_user["id"])
    return pages


@router.post("", response_model=PageResponse, status_code=201)
def create_page(page: PageCreate, current_user: dict = Depends(get_current_user)):
    """Create a new page."""
    created, error = page_service.create_page(page.name, current_user["id"], page.shared_with)
    if error:
        raise HTTPException(status_code=409, detail=error)
    return created


@router.put("/{page_id}", response_model=PageResponse)
def update_page(page_id: str, page: PageUpdate, current_user: dict = Depends(get_current_user)):
    """Update a page (only creator can update)."""
    # Check if user is the creator
    from database.mongodb import get_pages_collection
    existing = get_pages_collection().find_one({"_id": page_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Page not found")
    if str(existing["created_by"]) != current_user["id"]:
        raise HTTPException(status_code=403, detail="Only the creator can update this page")

    updated, error = page_service.update_page(page_id, page.name, page.shared_with)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return updated


@router.delete("/{page_id}")
def delete_page(page_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a page. Tasks are reassigned to 'Uncategorized'."""
    success, message = page_service.delete_page(page_id, current_user["id"])
    if not success:
        if "Only the creator" in message:
            raise HTTPException(status_code=403, detail=message)
        raise HTTPException(status_code=404, detail=message)
    return {"message": message}
