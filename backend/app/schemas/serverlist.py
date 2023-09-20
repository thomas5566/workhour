from pydantic import BaseModel


class ServerListBase(BaseModel):
    id: int
    branch_id: int    
    server_name: str
    server_ip: str
    server_location: str
    server_acc: str
    server_pass: str
    server_remark: str


class ServerList(ServerListBase):
    id: int

    class Config:
        orm_mode = True


class ServerListByBranchId(BaseModel):
    id: int
    branch_id: int    
    server_name: str
    server_ip: str
    server_location: str
    server_acc: str
    server_pass: str
    server_remark: str

    class Config:
        orm_mode = True

