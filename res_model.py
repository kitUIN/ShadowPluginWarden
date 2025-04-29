
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from typing import Generic, List, TypeVar  

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    limit: int
    pages: int
    items: List[T]

class AssetModel(BaseModel):
    id: int
    github_id: int
    name: str
    content_type: str
    state: str
    size: int
    download_count: int
    created_at: datetime
    updated_at: datetime
    browser_download_url: str
    model_config = ConfigDict(from_attributes=True)

class AuthorModel(BaseModel):
    id: int
    github_id: int
    login: str
    avatar_url: str
    html_url: str
    type: str
    model_config = ConfigDict(from_attributes=True)
    
class ReleaseModel(BaseModel):
    id: int
    github_id: int
    tag_name: str
    name: str
    body: Optional[str] = None
    draft: bool
    prerelease: bool
    created_at: datetime
    published_at: Optional[datetime] = None
    html_url: str
    tarball_url: str
    zipball_url: str
    assets: List[AssetModel] = []
    author: Optional[AuthorModel] = None
    model_config = ConfigDict(from_attributes=True)
    


class RepositoryBasicModel(BaseModel):
    id: int
    name: str
    full_name: str
    html_url: str
    plugin: Dict
    releases: List[str] = []

class RepositoryModel(RepositoryBasicModel): 
    releases: List[ReleaseModel] = []