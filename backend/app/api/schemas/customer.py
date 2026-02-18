from pydantic import BaseModel, Field, ConfigDict


class CustomerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255, description="Customer name")


class CustomerResponse(BaseModel):
    id: int
    name: str
    
    model_config = ConfigDict(from_attributes=True)