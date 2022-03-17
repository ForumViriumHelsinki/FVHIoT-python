from typing import List, Dict, Optional

from pydantic import BaseModel


class Lrr(BaseModel):
    Lrrid: str  # "FF01A275",
    Chain: int  # 0,
    LrrRSSI: float  # -96.0,
    LrrSNR: float  # 13.0,
    LrrESP: float  # -96.212387


class Lrrs(BaseModel):
    __root__: Dict[str, List[Lrr]]


class Alr(BaseModel):
    pro: str  # "declab/mb7386",
    ver: str  # "1"


class CustomerData(BaseModel):
    __root__: Dict[str, Alr]


class DevEuiUplink(BaseModel):
    """
    Complete DevEUI_uplink data packet from Thingpark system.
    """
    Time: str  # "2022-02-10T06:59:28.171+00:00",
    DevEUI: str  # "1234D57BA000ABCD",
    FPort: int  # 1,
    FCntUp: int  # 678,
    ADRbit: Optional[int]  # 1,
    MType: int  # 2,
    FCntDn: int  # 39,
    payload_hex: str  # "0218d700030394000f0a31",
    mic_hex: str  # "559b1a30",
    Lrcid: str  # "00000201",
    LrrRSSI: float  # -96.0,
    LrrSNR: float  # 13.0,
    LrrESP: float  # -96.212387,
    SpFact: int  # 7,
    SubBand: str  # "G2",
    Channel: str  # "LC7",
    DevLrrCnt: int  # 6,
    Lrrid: str  # "FF01A275",
    Late: int  # 0,
    LrrLAT: float  # 60.170341,
    LrrLON: float  # 24.948341,
    CustomerID: str  # "100001234",
    CustomerData: CustomerData  # {"alr": {"pro": "declab/mb7386", "ver": "1"}},
    ModelCfg: str  # "0",
    DevAddr: str  # "E002ABCD",
    TxPower: float  # 14.0,
    NbTrans: int  # 1,
    Frequency: float  # 867.7,
    DynamicClass: str  # "A"
    Lrrs: Lrrs
