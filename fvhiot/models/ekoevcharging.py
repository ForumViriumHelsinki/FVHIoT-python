"""
OCPP standard models for EKO EV charging.
"""
from enum import Enum
from typing import Any, Union

from pydantic import BaseModel, Field


class ContextEnum(str, Enum):
    InterruptionBegin = "Interruption.Begin"
    InterruptionEnd = "Interruption.End"
    SampleClock = "Sample.Clock"
    TransactionBegin = "Transaction.Begin"
    TransactionEnd = "Transaction.End"
    Trigger = "Trigger"
    Other = "Other"


class FormatEnum(str, Enum):
    Raw = "Raw"
    SignedData = "SignedData"


class MeasurandEnum(str, Enum):
    EnergyActiveExportRegister = "Energy.Active.Export.Register"
    EnergyActiveImportRegister = "Energy.Active.Import.Register"
    EnergyReactiveExportRegister = "Energy.Reactive.Export.Register"
    EnergyReactiveImportRegister = "Energy.Reactive.Import.Register"
    EnergyActiveExportInterval = "Energy.Active.Export.Interval"
    EnergyActiveImportInterval = "Energy.Active.Import.Interval"
    EnergyReactiveExportInterval = "Energy.Reactive.Export.Interval"
    EnergyReactiveImportInterval = "Energy.Reactive.Import.Interval"
    PowerActiveExport = "Power.Active.Export"
    PowerActiveImport = "Power.Active.Import"
    PowerOffered = "Power.Offered"
    PowerReactiveExport = "Power.Reactive.Export"
    PowerReactiveImport = "Power.Reactive.Import"
    PowerFactor = "Power.Factor"
    CurrentImport = "Current.Import"
    CurrentExport = "Current.Export"
    CurrentOffered = "Current.Offered"
    Voltage = "Voltage"
    Frequency = "Frequency"
    Temperature = "Temperature"
    SoC = "SoC"
    RPM = "RPM"


class PhaseEnum(str, Enum):
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    N = "N"
    L1_N = "L1-N"
    L2_N = "L2-N"
    L3_N = "L3-N"
    L1_L2 = "L1-L2"
    L2_L3 = "L2-L3"
    L3_L1 = "L3-L1"


class LocationEnum(str, Enum):
    Cable = "Cable"
    EV = "EV"
    Inlet = "Inlet"
    Outlet = "Outlet"
    Body = "Body"


class UnitEnum(str, Enum):
    Wh = "Wh"
    kWh = "kWh"
    varh = "varh"
    kvarh = "kvarh"
    W = "W"
    kW = "kW"
    VA = "VA"
    kVa = "kVA"
    var = "var"
    kvar = "kvar"
    A = "A"
    V = "V"
    K = "K"
    Celcius = "Celcius"
    Fahrenheit = "Fahrenheit"
    Percent = "Percent"


class ErrorCodeEnum(str, Enum):
    ConnectorLockFailure = "ConnectorLockFailure"
    EVCommunicationError = "EVCommunicationError"
    GroundFailure = "GroundFailure"
    HighTemperature = "HighTemperature"
    InternalError = "InternalError"
    LocalListConflict = "LocalListConflict"
    NoError = "NoError"
    OtherError = "OtherError"
    OverCurrentFailure = "OverCurrentFailure"
    PowerMeterFailure = "PowerMeterFailure"
    PowerSwitchFailure = "PowerSwitchFailure"
    ReaderFailure = "ReaderFailure"
    ResetFailure = "ResetFailure"
    UnderVoltage = "UnderVoltage"
    OverVoltage = "OverVoltage"
    WeakSignal = "WeakSignal"


class StatusEnum(str, Enum):
    Available = "Available"
    Preparing = "Preparing"
    Charging = "Charging"
    SuspendedEVSE = "SuspendedEVSE"
    SuspendedEV = "SuspendedEV"
    Finishing = "Finishing"
    Reserved = "Reserved"
    Unavailable = "Unavailable"
    Faulted = "Faulted"


class SampleValue(BaseModel):
    context: ContextEnum
    format: FormatEnum
    measurand: MeasurandEnum
    phase: PhaseEnum
    location: LocationEnum
    unit: UnitEnum
    value: str


class MeterValue(BaseModel):
    timestamp: str  # "2021-08-16T19:21:04Z"
    sampledValue: SampleValue  # see above for a more thorough modeling of this


class MeterValues(BaseModel):
    connectorId: int
    meterValue: MeterValue
    transactionId: int


class StatusNotification(BaseModel):
    connectorId: int
    errorCode: ErrorCodeEnum
    info: str
    status: StatusEnum
    timestamp: str = Field(alias="packet_timestamp")  # "2021-08-16T19:21:04Z"
    vendorId: str
    vendorErrorCode: str

    class Config:
        allow_population_by_field_name = True


class OCPP(BaseModel):
    _id: str
    messageType: str
    data: Union[MeterValues, StatusNotification, Any] = Field(
        alias="payload"
    )  # we may receive websocket errors, etc. which are not yet modeled => allow any
    chargeBoxId: str = None
    chargeBoxGroupId: str
    chargePointId: str
    chargePointGroupId: str
    uniqueId: int = None
    ocppStandard: str
    centralSystemResponse: Any = None
    createdAt: str = Field(alias="packet_timestamp")  # "2021-08-16T19:21:04Z"

    class Config:
        allow_population_by_field_name = True
