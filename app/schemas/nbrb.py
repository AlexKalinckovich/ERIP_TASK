from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

CurrencyAbbreviation = Annotated[str, Field(pattern=r"^[A-Z]{3}$")]
CurrencyNumericCode = Annotated[str, Field(pattern=r"^\d{3}$")]
NBRBRateValue = Annotated[
    Decimal,
    Field(gt=0, max_digits=12, decimal_places=4),
]


class NBRBRate(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )

    cur_id: int = Field(..., alias="Cur_ID")
    cur_code: CurrencyNumericCode | None = Field(default=None, alias="Cur_Code")
    date: datetime = Field(..., alias="Date")
    cur_abbreviation: CurrencyAbbreviation = Field(..., alias="Cur_Abbreviation")
    cur_scale: int = Field(..., gt=0, alias="Cur_Scale")
    cur_name: str = Field(..., alias="Cur_Name")
    cur_official_rate: NBRBRateValue = Field(..., alias="Cur_OfficialRate")


class NBRBCurrency(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )

    cur_id: int = Field(..., alias="Cur_ID")
    cur_parent_id: int = Field(..., alias="Cur_ParentID")
    cur_code: CurrencyNumericCode = Field(..., alias="Cur_Code")
    cur_abbreviation: CurrencyAbbreviation = Field(..., alias="Cur_Abbreviation")
    cur_name: str = Field(..., alias="Cur_Name")
    cur_name_bel: str = Field(..., alias="Cur_Name_Bel")
    cur_name_eng: str = Field(..., alias="Cur_Name_Eng")
    cur_quot_name: str = Field(..., alias="Cur_QuotName")
    cur_quot_name_bel: str = Field(..., alias="Cur_QuotName_Bel")
    cur_quot_name_eng: str = Field(..., alias="Cur_QuotName_Eng")
    cur_name_multi: str = Field(..., alias="Cur_NameMulti")
    cur_name_bel_multi: str = Field(..., alias="Cur_Name_BelMulti")
    cur_name_eng_multi: str = Field(..., alias="Cur_Name_EngMulti")
    cur_scale: int = Field(..., gt=0, alias="Cur_Scale")
    cur_periodicity: int = Field(..., ge=0, alias="Cur_Periodicity")
    cur_date_start: datetime = Field(..., alias="Cur_DateStart")
    cur_date_end: datetime = Field(..., alias="Cur_DateEnd")
