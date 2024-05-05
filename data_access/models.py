from enum import Enum
from typing import List, Union
from pydantic import BaseModel, Field
from pydantic_xml import BaseXmlModel

class docTypeModel(BaseXmlModel):
    documentType: str = Field(..., min_length=1)

class InvoiceItem(BaseXmlModel, tag="InvoiceItem"):
    description: str = Field(..., min_length=1)
    size: str = Field(..., min_length=1)
    finish: str = Field(..., min_length=1)
    quantity: int
    unitPrice: float
    total: float

    def to_dict(self):
        return {
            "description": self.description,
            "size": self.size,
            "finish": self.finish,
            "quantity": self.quantity,
            "unitPrice": self.unitPrice,
            "total": self.total
        }

class InvoiceSummary(BaseXmlModel, tag="InvoiceSummary"):
    subTotal: float
    discount: float
    totalLessDiscount: float
    taxRate: float
    totalTax: float
    balanceDue: float

    def to_dict(self):
        return {
            "subTotal": self.subTotal,
            "discount": self.discount,
            "totalLessDiscount": self.totalLessDiscount,
            "taxRate": self.taxRate,
            "totalTax": self.totalTax,
            "balanceDue": self.balanceDue
        }

class InvoiceModel(docTypeModel, tag="Invoice"):
    documentType: str = Field(..., min_length=1)
    companyName: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)
    website: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    billToAddress: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)
    billToPhone: str = Field(..., min_length=1)
    number: int
    date: str = Field(..., min_length=1)
    dueDate: str = Field(..., min_length=1)
    items: List[InvoiceItem]
    summary: InvoiceSummary
    instruction: str = Field(..., min_length=1)
    warranty: str = Field(..., min_length=1)

    class Config:
        arbitrary_types_allowed = True
    def to_dict(self):
        return {
            "documentType": self.documentType,
            "companyName": self.companyName,
            "address": self.address,
            "website": self.website,
            "phone": self.phone,
            "name": self.name,
            "billToAddress": self.billToAddress,
            "email": self.email,
            "billToPhone": self.billToPhone,
            "number": self.number,
            "date": self.date,
            "dueDate": self.dueDate,
            'items': [item.to_dict() for item in self.items],
            "summary": self.summary.dict(),
            "instruction": self.instruction,
            "warranty": self.warranty
        }

class EarningItem(BaseXmlModel, tag="EarningItem"):
    description: str = Field(..., min_length=1)
    amount: float

    def to_dict(self):
        return {
            "description": self.description,
            "amount": self.amount
        }

class DeductionItem(BaseXmlModel, tag="DeductionItem"):
    description: str = Field(..., min_length=1)
    amount: float

    def to_dict(self):
        return {
            "description": self.description,
            "amount": self.amount
        }

class PaycheckModel(docTypeModel, tag="Paycheck"):
    documentType: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    periodStart: str = Field(..., min_length=1)
    periodEnd: str = Field(..., min_length=1)
    processingDate: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    position: str = Field(..., min_length=1)
    department: str = Field(..., min_length=1)
    earnings: EarningItem
    deductions: DeductionItem
    netPay: float
    companyName: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self):

        return {
            "documentType": self.documentType,
            "title": self.title,
            "periodStart": self.periodStart,
            "periodEnd": self.periodEnd,
            "processingDate": self.processingDate,
            "name": self.name,
            "position": self.position,
            "department": self.department,
            "earnings": self.earnings.dict(),
            "deductions": self.deductions.dict(),
            "netPay": self.netPay,
            "companyName": self.companyName,
            "address": self.address
        }
class storageEnum(str, Enum):
    TEMP = 'temp'
    PERM = 'perm'
class FileModel(BaseModel):
    data: Union[InvoiceModel, PaycheckModel]
    storage_type: storageEnum = storageEnum.TEMP.value

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self):
        return {
            "data": self.data.to_dict(),
            "storage_type": self.storage_type
        }
